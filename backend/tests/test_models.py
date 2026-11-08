"""Model validation tests (step 1)."""

import pytest
from pydantic import ValidationError

from backend.models import Digest, Post, Source, Story, StorySource


def test_source_accepts_valid_tier() -> None:
    s = Source(id="bbc", name="BBC", url="https://x", tier="trustworthy")
    assert s.tier == "trustworthy"


def test_source_rejects_unknown_tier() -> None:
    with pytest.raises(ValidationError):
        Source(id="x", name="X", url="https://x", tier="bogus")


def test_post_parses_full_dict() -> None:
    p = Post(
        post_id="123",
        source_id="bbc",
        source_name="BBC",
        source_tier="trustworthy",
        url="https://facebook.com/123",
        text="hello",
        likes=1,
        comments=2,
        shares=3,
        engagement=6,
        timestamp=1760000000,
        first_seen="2026-11-08T10:00:00+06:30",
        last_updated="2026-11-08T10:00:00+06:30",
    )
    assert p.engagement == 6
    assert p.post_id == "123"


def test_post_requires_text() -> None:
    with pytest.raises(ValidationError):
        Post(post_id="1", source_id="s", source_name="S", source_tier="tabloid", url="u", text="")


def test_digest_round_trip() -> None:
    story = Story(
        id="story-1",
        title="ခေါင်းစဉ်",
        summary="အနှစ်ချုပ်",
        tags=["tea"],
        sources=[
            StorySource(
                source_id="s1",
                source_name="S",
                source_tier="tabloid",
                post_url="https://facebook.com/1",
            )
        ],
        engagement=10,
        first_seen="2026-11-08T10:00:00+06:30",
        last_updated="2026-11-08T10:00:00+06:30",
    )
    d = Digest(date="2026-11-08", generated_at="now", stories=[story])
    assert d.schema_version == 1
    assert d.stories[0].tags == ["tea"]
    parsed = Digest.model_validate_json(d.model_dump_json())
    assert parsed == d
