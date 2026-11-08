"""Repository tests (step 2): upsert idempotency + day window queries."""

from datetime import date
from pathlib import Path

from backend.models import Post
from backend.repo import PostRepo
from backend.timeutil import day_bounds


def make_post(post_id: str, timestamp: int, engagement: int = 0) -> Post:
    return Post(
        post_id=post_id,
        source_id="bbc",
        source_name="BBC",
        source_tier="trustworthy",
        url=f"https://facebook.com/{post_id}",
        text="text",
        engagement=engagement,
        likes=engagement,
        timestamp=timestamp,
        first_seen="2026-11-08T10:00:00+06:30",
        last_updated="2026-11-08T10:00:00+06:30",
    )


def test_upsert_same_post_twice_keeps_one_row(tmp_path: Path) -> None:
    repo = PostRepo(tmp_path / "test.db")
    post = make_post("1", 1760000000, engagement=5)
    repo.upsert_posts([post])
    repo.upsert_posts([post])
    assert repo.count() == 1


def test_upsert_updates_engagement_preserves_first_seen(tmp_path: Path) -> None:
    repo = PostRepo(tmp_path / "test.db")
    first = make_post("1", 1760000000, engagement=5)
    first.last_updated = "2026-11-08T10:00:00+06:30"
    repo.upsert_posts([first])

    refetch = make_post("1", 1760000000, engagement=99)
    refetch.first_seen = "2026-11-08T20:00:00+06:30"  # must be ignored on conflict
    refetch.last_updated = "2026-11-08T20:00:00+06:30"
    repo.upsert_posts([refetch])

    posts = repo.get_posts_for_day(date(2025, 10, 9))
    assert len(posts) == 1
    assert posts[0].engagement == 99
    assert posts[0].first_seen == "2026-11-08T10:00:00+06:30"
    assert posts[0].last_updated == "2026-11-08T20:00:00+06:30"


def test_upsert_counts_new_and_updated(tmp_path: Path) -> None:
    repo = PostRepo(tmp_path / "test.db")
    new, updated = repo.upsert_posts([make_post("1", 1760000000), make_post("2", 1760000001)])
    assert (new, updated) == (2, 0)
    new, updated = repo.upsert_posts([make_post("2", 1760000001), make_post("3", 1760000002)])
    assert (new, updated) == (1, 1)
    assert repo.count() == 3


def test_upsert_empty_list_returns_zeroes(tmp_path: Path) -> None:
    repo = PostRepo(tmp_path / "test.db")
    assert repo.upsert_posts([]) == (0, 0)


def test_get_posts_for_day_filters_window(tmp_path: Path) -> None:
    repo = PostRepo(tmp_path / "test.db")
    start, end = day_bounds(date(2026, 11, 8))
    repo.upsert_posts(
        [
            make_post("in-1", start),  # first second of the day
            make_post("in-2", end - 1),  # last second of the day
            make_post("out-1", start - 1),  # yesterday
            make_post("out-2", end),  # tomorrow
        ]
    )
    posts = repo.get_posts_for_day(date(2026, 11, 8))
    assert sorted(p.post_id for p in posts) == ["in-1", "in-2"]


def test_get_posts_for_day_orders_by_engagement(tmp_path: Path) -> None:
    repo = PostRepo(tmp_path / "test.db")
    start, _ = day_bounds(date(2026, 11, 8))
    repo.upsert_posts(
        [make_post("low", start, engagement=1), make_post("high", start, engagement=100)]
    )
    posts = repo.get_posts_for_day(date(2026, 11, 8))
    assert [p.post_id for p in posts] == ["high", "low"]
