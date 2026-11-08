"""SQLite post store behind a thin repository interface.

Jobs never touch SQL; swapping the storage engine would not touch job code.
"""

import sqlite3
from datetime import date
from pathlib import Path

from backend.models import Post
from backend.timeutil import day_bounds

_COLUMNS = [
    "post_id",
    "source_id",
    "source_name",
    "source_tier",
    "url",
    "text",
    "likes",
    "comments",
    "shares",
    "engagement",
    "timestamp",
    "first_seen",
    "last_updated",
]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    post_id      TEXT PRIMARY KEY,
    source_id    TEXT NOT NULL,
    source_name  TEXT NOT NULL,
    source_tier  TEXT NOT NULL,
    url          TEXT NOT NULL,
    text         TEXT NOT NULL,
    likes        INTEGER NOT NULL,
    comments     INTEGER NOT NULL,
    shares       INTEGER NOT NULL,
    engagement   INTEGER NOT NULL,
    timestamp    INTEGER NOT NULL,
    first_seen   TEXT NOT NULL,
    last_updated TEXT NOT NULL
)
"""

_UPSERT = """
INSERT INTO posts ({cols}) VALUES ({ph})
ON CONFLICT(post_id) DO UPDATE SET
    likes = excluded.likes,
    comments = excluded.comments,
    shares = excluded.shares,
    engagement = excluded.engagement,
    timestamp = excluded.timestamp,
    last_updated = excluded.last_updated
""".format(cols=", ".join(_COLUMNS), ph=", ".join("?" * len(_COLUMNS)))


class PostRepo:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def upsert_posts(self, posts: list[Post]) -> tuple[int, int]:
        """Insert new posts, update engagement on refetch. first_seen never changes.

        Returns (new, updated) counts by unique post id.
        """
        if not posts:
            return 0, 0
        ids = [p.post_id for p in posts]
        existing: set[str] = set()
        for i in range(0, len(ids), 500):
            chunk = ids[i : i + 500]
            rows = self._conn.execute(
                f"SELECT post_id FROM posts WHERE post_id IN ({','.join('?' * len(chunk))})",
                chunk,
            )
            existing.update(r[0] for r in rows)
        self._conn.executemany(
            _UPSERT,
            [tuple(p.model_dump()[c] for c in _COLUMNS) for p in posts],
        )
        self._conn.commit()
        unique = set(ids)
        return len(unique - existing), len(unique & existing)

    def get_posts_for_day(self, day: date) -> list[Post]:
        """All posts timestamped within the Myanmar-calendar day, top engagement first."""
        start, end = day_bounds(day)
        rows = self._conn.execute(
            f"SELECT {', '.join(_COLUMNS)} FROM posts"
            " WHERE timestamp >= ? AND timestamp < ?"
            " ORDER BY engagement DESC",
            (start, end),
        ).fetchall()
        return [Post.model_validate(dict(zip(_COLUMNS, row))) for row in rows]

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0])
