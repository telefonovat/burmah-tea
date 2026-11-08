"""Mechanical tag tests (step 5): confirmed + popular rules, tea coexistence."""

from backend.jobs.digest import apply_tags
from backend.models import Story, StorySource


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
