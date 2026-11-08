"""Mechanical tag tests (step 5): confirmed + popular rules, tea coexistence."""

from backend.jobs.digest import apply_tags, build_stories
from backend.models import Post, Story, StorySource


def make_story(engagement: int, tiers: list[str], tea: bool = False) -> Story:
    sources = [
        StorySource(
            source_id=f"s{i}",
            source_name=f"S{i}",
            source_tier=tier,  # type: ignore[arg-type]
            post_url=f"https://facebook.com/{i}",
        )
        for i, tier in enumerate(tiers)
    ]
    return Story(
        id="story-x",
        title="t",
        summary="s",
        tags=["tea"] if tea else [],
        sources=sources,
        engagement=engagement,
        first_seen="a",
        last_updated="b",
    )


def test_confirmed_needs_two_distinct_trustworthy() -> None:
    story = make_story(10, ["trustworthy", "trustworthy"])
    apply_tags([story], fraction=0.1)
    assert "confirmed" in story.tags


def test_confirmed_not_one_trustworthy() -> None:
    story = make_story(10, ["trustworthy", "tabloid"])
    apply_tags([story], fraction=0.1)
    assert "confirmed" not in story.tags


def test_confirmed_not_same_source_twice() -> None:
    story = make_story(10, ["trustworthy"])
    story.sources.append(story.sources[0].model_copy())
    apply_tags([story], fraction=0.1)
    assert "confirmed" not in story.tags


def test_popular_top_decile_of_30() -> None:
    stories = [make_story(e, ["tabloid"]) for e in range(1, 31)]
    apply_tags(stories, fraction=0.1)
    popular = [s.engagement for s in stories if "popular" in s.tags]
    assert sorted(popular, reverse=True) == [30, 29, 28]


def test_popular_min_one() -> None:
    stories = [make_story(e, ["tabloid"]) for e in range(1, 11)]
    apply_tags(stories, fraction=0.1)
    assert [s.engagement for s in stories if "popular" in s.tags] == [10]
    only = [make_story(5, ["tabloid"])]
    apply_tags(only, fraction=0.1)
    assert "popular" in only[0].tags


def test_tags_ordered_confirmed_popular_tea() -> None:
    story = make_story(100, ["trustworthy", "trustworthy"], tea=True)
    apply_tags([story], fraction=0.1)
    assert story.tags == ["confirmed", "popular", "tea"]


def make_post(post_id: str) -> Post:
    return Post(
        post_id=post_id,
        source_id="s1",
        source_name="S1",
        source_tier="trustworthy",
        url=f"https://facebook.com/{post_id}",
        text="text",
        engagement=5,
        first_seen="a",
        last_updated="b",
    )


def test_build_stories_maps_en_fields() -> None:
    posts = [make_post("1"), make_post("2")]
    topics = [
        {
            "title": "ခေါင်းစဉ်",
            "summary": "အနှစ်ချုပ်",
            "title_en": "Headline",
            "summary_en": "Summary",
            "post_ids": ["1", "2"],
            "tea": False,
        }
    ]
    stories = build_stories(posts, topics)
    assert len(stories) == 1
    assert stories[0].title_en == "Headline"
    assert stories[0].summary_en == "Summary"


def test_build_stories_en_fields_optional() -> None:
    """LLM topics without en keys must still produce stories."""
    posts = [make_post("1")]
    topics = [{"title": "ခေါင်းစဉ်", "summary": "အနှစ်ချုပ်", "post_ids": ["1"], "tea": False}]
    stories = build_stories(posts, topics)
    assert stories[0].title_en == ""
    assert stories[0].summary_en == ""
