"""Digest job: day's posts -> one LLM clustering call -> data/digests/today.json.

Recomputes the day's digest from scratch from all posts of the day. Topics are
always re-derived, never merged with prior output. today.json is a derived view;
the post store is the source of truth.

Run: uv run --project backend python -m backend.jobs.digest
"""

import json
import re
from datetime import date
from math import ceil

from openai import OpenAI

from backend.config import DATA_DIR, settings
from backend.models import Digest, Post, Story, StorySource
from backend.repo import PostRepo
from backend.runlog import run_logged
from backend.timeutil import now_mmt_iso, today_mmt

DB_FILE = DATA_DIR / "posts.db"
OUTPUT_FILE = DATA_DIR / "digests" / "today.json"

# Cap each post's text so a few long posts can't crowd out the rest.
MAX_POST_CHARS = 1000

SYSTEM_PROMPT = """You are the editor of a daily Burmese news digest. You receive today's Facebook \
posts from Burmese pages, each with its source page, trust tier (trustworthy, subpar, tabloid, \
celebrity) and engagement.

Cluster the posts into topics: posts covering the same event or story belong together. A topic can \
be a single notable post. Ignore spam and empty items.

For each topic, respond with a JSON object:
- "title": short Burmese headline
- "summary": 2-4 sentence Burmese summary. Attribute claims to sources with tier-appropriate \
hedging, e.g. "according to X, a tabloid page" for unverified claims. Never state unverified \
claims as confirmed fact.
- "title_en": the same headline in English
- "summary_en": the same summary in English, with the same attribution and hedging
- "post_ids": the post ids belonging to this topic (every post belongs to at most one topic; \
leave junk posts out entirely)
- "tea": true if the topic is gossip, celebrity rumor, or entertainment speculation rather than \
news, false otherwise. A trustworthy outlet can carry tea.

Respond with ONLY a JSON array of these objects, no other text."""


def build_user_prompt(posts: list[Post]) -> str:
    lines = []
    for p in posts:
        lines.append(
            f"[{p.post_id}] ({p.source_name}, tier: {p.source_tier}, engagement: {p.engagement})\n"
            f"{p.text[:MAX_POST_CHARS]}"
        )
    return "\n\n".join(lines)


def call_llm(posts: list[Post]) -> list[dict]:
    client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    completion = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(posts)},
        ],
    )
    content = completion.choices[0].message.content or ""
    # Models sometimes wrap JSON in markdown fences; strip them.
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    topics = json.loads(content)
    if not isinstance(topics, list):
        raise ValueError("LLM response is not a JSON array")
    return topics


def build_stories(posts: list[Post], topics: list[dict]) -> list[Story]:
    """Map LLM topics to Story objects; posts are the source of truth for all metadata."""
    by_id = {p.post_id: p for p in posts}
    stories: list[Story] = []
    for i, topic in enumerate(topics, start=1):
        # LLMs sometimes emit numeric ids as JSON numbers; coerce before matching.
        topic_posts = [by_id[str(pid)] for pid in topic.get("post_ids", []) if str(pid) in by_id]
        if not topic_posts:
            continue
        sources: list[StorySource] = []
        seen_sources: set[str] = set()
        for p in topic_posts:
            if p.source_id not in seen_sources:
                seen_sources.add(p.source_id)
                sources.append(
                    StorySource(
                        source_id=p.source_id,
                        source_name=p.source_name,
                        source_tier=p.source_tier,
                        post_url=p.url,
                    )
                )
        tags = ["tea"] if topic.get("tea") else []
        stories.append(
            Story(
                id=f"story-{i}",
                title=topic.get("title", ""),
                summary=topic.get("summary", ""),
                title_en=topic.get("title_en", ""),
                summary_en=topic.get("summary_en", ""),
                tags=tags,
                sources=sources,
                engagement=sum(p.engagement for p in topic_posts),
                first_seen=min(p.first_seen for p in topic_posts),
                last_updated=max(p.last_updated for p in topic_posts),
            )
        )
    return stories


_TAG_ORDER = {"confirmed": 0, "popular": 1, "tea": 2}


def apply_tags(stories: list[Story], fraction: float) -> None:
    """Mechanical tags, in place. The LLM decides what a story is;
    arithmetic decides how true or popular it is.

    - confirmed: posts from at least 2 distinct trustworthy-tier sources.
    - popular: engagement in the top `fraction` of today's story distribution.
    """
    for story in stories:
        trustworthy = {s.source_id for s in story.sources if s.source_tier == "trustworthy"}
        if len(trustworthy) >= 2:
            story.tags.append("confirmed")
    if stories:
        # epsilon kills float noise: 30 * 0.1 == 3.0000000000000004
        k = max(1, ceil(len(stories) * fraction - 1e-9))
        for story in sorted(stories, key=lambda s: s.engagement, reverse=True)[:k]:
            story.tags.append("popular")
    for story in stories:
        story.tags = sorted(set(story.tags), key=lambda t: _TAG_ORDER[t])


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--day", help="digest day as YYYY-MM-DD (Myanmar calendar); default today"
    )
    args = parser.parse_args()

    day = date.fromisoformat(args.day) if args.day else today_mmt()

    def run() -> dict[str, int]:
        posts = PostRepo(DB_FILE).get_posts_for_day(day)
        if not posts:
            raise RuntimeError(f"No posts for {day} in {DB_FILE}. Run the fetch job first.")
        print(f"{len(posts)} posts for {day} -> clustering via {settings.llm_model}")

        topics = call_llm(posts)
        stories = build_stories(posts, topics)
        if not stories:
            raise RuntimeError(
                f"LLM returned {len(topics)} topics but none matched a known post id"
            )
        print(f"{len(stories)} stories")
        apply_tags(stories, settings.popular_top_fraction)

        digest = Digest(
            date=day.isoformat(),
            generated_at=now_mmt_iso(),
            stories=stories,
        )
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(
            digest.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(f"Wrote {OUTPUT_FILE}")
        return {
            "posts": len(posts),
            "topics": len(topics),
            "stories": len(stories),
            "confirmed": sum("confirmed" in s.tags for s in stories),
            "popular": sum("popular" in s.tags for s in stories),
            "tea": sum("tea" in s.tags for s in stories),
        }

    run_logged("digest", day.isoformat(), run)


if __name__ == "__main__":
    main()
