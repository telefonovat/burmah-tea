"""Fetch job: Apify pages -> normalised posts -> SQLite store. No LLM calls.

--no-fetch reads the saved raw snapshot so development never spends Apify credits.
Idempotent: upsert keyed by post ID, engagement updated on refetch.

Run: uv run --project backend python -m backend.jobs.fetch [--no-fetch]
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apify_client import ApifyClient

from backend.config import DATA_DIR, settings
from backend.models import Post, Source
from backend.repo import PostRepo
from backend.runlog import run_logged
from backend.sources import load_sources
from backend.timeutil import MMT, now_mmt_iso, today_mmt

ACTOR_ID = "apify/facebook-posts-scraper"
FIXTURE_FILE = DATA_DIR / "fixtures" / "raw-2026-11-08.json"
DB_FILE = DATA_DIR / "posts.db"

# Cap posts per page so a runaway page can't burn the Apify credit.
RESULTS_LIMIT = 50


def normalise(item: dict, source: Source, now_iso: str) -> Post | None:
    """Map a raw actor item to a Post; None if the item is unusable."""
    text = (item.get("text") or "").strip()
    post_id = item.get("postId") or ""
    url = item.get("url") or item.get("topLevelUrl") or ""
    if not text or not (post_id or url):
        return None

    likes = item.get("likes") or 0
    comments = item.get("comments") or 0
    shares = item.get("shares") or 0

    return Post(
        post_id=post_id or url,
        source_id=source.id,
        source_name=source.name,
        source_tier=source.tier,
        url=url,
        text=text,
        likes=likes,
        comments=comments,
        shares=shares,
        engagement=likes + comments + shares,
        timestamp=item.get("timestamp") or 0,
        first_seen=now_iso,
        last_updated=now_iso,
    )


def fetch_raw(sources: list[Source]) -> list[dict]:
    """Live Apify run over all source pages, windowed to the last 24h MMT."""
    if not settings.apify_token:
        raise SystemExit("APIFY_TOKEN missing. Add it to backend/.env")

    now_mmt = datetime.now(MMT)
    start_mmt = now_mmt - timedelta(hours=24)
    start_utc_iso = start_mmt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Window: {start_mmt:%Y-%m-%d %H:%M} to {now_mmt:%Y-%m-%d %H:%M} MMT")

    client = ApifyClient(token=settings.apify_token)
    run = client.actor(ACTOR_ID).call(
        run_input={
            "startUrls": [{"url": s.url} for s in sources],
            "resultsLimit": RESULTS_LIMIT,
            "onlyPostsNewerThan": start_utc_iso,
        }
    )
    return list(client.dataset(run.default_dataset_id).iterate_items())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-fetch", action="store_true", help="read the saved raw fixture instead of Apify"
    )
    parser.add_argument(
        "--fixture", type=Path, default=FIXTURE_FILE, help="fixture path for --no-fetch"
    )
    args = parser.parse_args()

    def run() -> dict[str, int]:
        sources = load_sources()
        by_url = {s.url: s for s in sources}
        now_iso = now_mmt_iso()

        if args.no_fetch:
            raw = json.loads(args.fixture.read_text(encoding="utf-8"))
            print(f"Fixture: {len(raw)} raw items from {args.fixture}")
        else:
            print(f"Fetching {len(sources)} sources from Apify...")
            raw = fetch_raw(sources)
            # Raw snapshot: lets all later work re-run normalisation without Apify spend.
            snapshot = DATA_DIR / "fixtures" / f"raw-{today_mmt().isoformat()}.json"
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_text(
                json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"Raw snapshot: {len(raw)} items -> {snapshot}")

        posts: list[Post] = []
        skipped_unmatched = 0
        for item in raw:
            # Every post inherits its source tier at fetch time.
            source = by_url.get(item.get("inputUrl") or item.get("facebookUrl") or "")
            if source is None:
                skipped_unmatched += 1
                continue
            post = normalise(item, source, now_iso)
            if post is not None:
                posts.append(post)

        new, updated = PostRepo(DB_FILE).upsert_posts(posts)
        print(f"Upserted {len(posts)} posts -> {DB_FILE} ({new} new, {updated} updated)")
        if skipped_unmatched:
            print(f"Skipped {skipped_unmatched} items with no matching source URL")
        return {
            "posts_fetched": len(raw),
            "posts_new": new,
            "posts_updated": updated,
            "skipped_unmatched": skipped_unmatched,
        }

    run_logged("fetch", today_mmt().isoformat(), run)


if __name__ == "__main__":
    main()
