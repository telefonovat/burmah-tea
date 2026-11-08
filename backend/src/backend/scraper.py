"""Scrape Facebook posts from the last 24h (Myanmar Time) into digest.today.test.json.

Run: uv run --project backend python -m backend.scraper
"""

import json
import yaml
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apify_client import ApifyClient
from pydantic import BaseModel

from backend.main import DATA_DIR, settings

ACTOR_ID = "apify/facebook-posts-scraper"
SOURCES_FILE = Path(__file__).parents[3] / "data" / "sources.yaml"
OUTPUT_FILE = DATA_DIR / "digest.today.test.json"
FIXTURE_FILE = DATA_DIR / "fixtures" / "raw-2026-11-08.json"


class Source(BaseModel):
    id: str
    name: str
    url: str
    tier: str


def load_sources() -> list[Source]:
    with SOURCES_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [Source(**s) for s in data["sources"]]

# Myanmar Time: UTC+6:30, no DST.
MMT = timezone(timedelta(hours=6, minutes=30))

# Cap posts per page so a runaway page can't burn the Apify credit.
RESULTS_LIMIT = 50





def normalise(item: dict, source: Source) -> dict | None:
    """Map a raw actor post to our clean schema; None if the post is unusable."""
    text = (item.get("text") or "").strip()
    if not text:
        return None

    likes = item.get("likes") or 0
    comments = item.get("comments") or 0
    shares = item.get("shares") or 0

    return {
        "source_id": source.id,
        "source_name": source.name,
        "source_tier": source.tier,
        "source_url": source.url,
        "page_name": item.get("user", {}).get("name") or item.get("pageName") or "",
        "page_url": item.get("facebookUrl") or item.get("inputUrl") or "",
        "url": item.get("url") or item.get("topLevelUrl") or "",
        "post_id": item.get("postId") or "",
        "time": item.get("time") or "",
        "timestamp": item.get("timestamp") or 0,
        "text": text,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "engagement": likes + comments + shares,
    }


def main() -> None:
    if not settings.apify_token:
        raise SystemExit("APIFY_TOKEN missing. Add it to backend/.env")

    sources = load_sources()

    # Window: last 24h in Myanmar Time, expressed in UTC for the actor filter.
    now_mmt = datetime.now(MMT)
    start_mmt = now_mmt - timedelta(hours=24)
    start_utc_iso = start_mmt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    start_ts = int(start_mmt.timestamp())
    print(f"Window: {start_mmt:%Y-%m-%d %H:%M} to {now_mmt:%Y-%m-%d %H:%M} MMT")
    print(f"Scraping {len(sources)} sources...")

    client = ApifyClient(token=settings.apify_token)
    run = client.actor(ACTOR_ID).call(
        run_input={
            "startUrls": [{"url": s.url} for s in sources],
            "resultsLimit": RESULTS_LIMIT,
            "onlyPostsNewerThan": start_utc_iso,
        }
    )

    raw = list(client.dataset(run.default_dataset_id).iterate_items())
    print(f"Fetched {len(raw)} raw posts")

    # Raw snapshot: lets all later work re-run normalisation without Apify spend.
    FIXTURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_FILE.write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Raw snapshot: {len(raw)} items -> {FIXTURE_FILE}")

    # Normalise, re-filter on the Burma window (actor filter is UTC-only), dedupe.
    posts: list[dict] = []
    seen: set[str] = set()
    dropped_no_text = dropped_out_of_window = dropped_dupes = 0

    for item in raw:
        # Match item to source by URL
        source = None
        input_url = item.get("inputUrl") or item.get("facebookUrl") or ""
        for s in sources:
            if s.url == input_url:
                source = s
                break
        if source is None:
            continue
        post = normalise(item, source)
        if post is None:
            dropped_no_text += 1
            continue
        if post["timestamp"] < start_ts:
            dropped_out_of_window += 1
            continue
        key = post["post_id"] or post["url"]
        if key in seen:
            dropped_dupes += 1
            continue
        seen.add(key)
        posts.append(post)

    posts.sort(key=lambda p: p["engagement"], reverse=True)

    OUTPUT_FILE.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"\nKept {len(posts)} posts -> {OUTPUT_FILE}")
    print(f"Dropped: {dropped_no_text} no text, {dropped_out_of_window} out of window, {dropped_dupes} dupes")
    by_source: dict[str, int] = {}
    for p in posts:
        by_source[p["source_name"]] = by_source.get(p["source_name"], 0) + 1
    for name, count in by_source.items():
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
