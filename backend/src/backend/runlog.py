"""Shared logging wrapper: append-only JSONL run log, one line per job run.

data/logs/runs.jsonl — success or failure. Failed jobs re-raise so the CLI
exits non-zero. Healthchecks pings (dead man's switch) wire in here later.
"""

import time
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from backend.config import DATA_DIR
from backend.timeutil import now_mmt_iso

RUN_LOG = DATA_DIR / "logs" / "runs.jsonl"


class RunLogLine(BaseModel):
    """One job run. counts is job-specific (posts fetched/new/updated, topics, ...)."""

    job: str  # fetch | digest | archive
    status: str  # success | failure
    started_at: str
    finished_at: str
    duration_s: float
    day: str
    counts: dict[str, int] = {}
    error: str | None = None


def append_log(line: RunLogLine, path: Path = RUN_LOG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line.model_dump_json() + "\n")


def run_logged(
    job: str, day: str, fn: Callable[[], dict[str, int]], path: Path = RUN_LOG
) -> None:
    """Run fn, append one log line, re-raise on failure so the process exits non-zero."""
    started_at = now_mmt_iso()
    t0 = time.monotonic()
    try:
        counts = fn()
    except Exception as e:
        append_log(
            RunLogLine(
                job=job,
                status="failure",
                started_at=started_at,
                finished_at=now_mmt_iso(),
                duration_s=round(time.monotonic() - t0, 3),
                day=day,
                error=f"{type(e).__name__}: {e}",
            ),
            path,
        )
        raise
    append_log(
        RunLogLine(
            job=job,
            status="success",
            started_at=started_at,
            finished_at=now_mmt_iso(),
            duration_s=round(time.monotonic() - t0, 3),
            day=day,
            counts=counts,
        ),
        path,
    )
