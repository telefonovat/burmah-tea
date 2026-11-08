"""Run log tests: append-only JSONL, success and failure lines."""

from pathlib import Path

import pytest

from backend.runlog import RunLogLine, append_log, run_logged


def test_append_log_writes_valid_jsonl(tmp_path: Path) -> None:
    log = tmp_path / "logs" / "runs.jsonl"
    append_log(RunLogLine(job="fetch", status="success", started_at="a", finished_at="b",
                          duration_s=1.0, day="2026-11-08", counts={"posts_new": 5}), log)
    append_log(RunLogLine(job="digest", status="failure", started_at="a", finished_at="b",
                          duration_s=2.0, day="2026-11-08", error="Boom: bad"), log)
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    first = RunLogLine.model_validate_json(lines[0])
    second = RunLogLine.model_validate_json(lines[1])
    assert first.counts == {"posts_new": 5}
    assert second.error == "Boom: bad"
    assert second.counts == {}


def test_run_logged_success_line(tmp_path: Path) -> None:
    log = tmp_path / "runs.jsonl"
    run_logged("fetch", "2026-11-08", lambda: {"posts_new": 3}, log)
    line = RunLogLine.model_validate_json(log.read_text(encoding="utf-8"))
    assert line.job == "fetch"
    assert line.status == "success"
    assert line.counts == {"posts_new": 3}
    assert line.error is None


def test_run_logged_failure_line_and_reraise(tmp_path: Path) -> None:
    log = tmp_path / "runs.jsonl"

    def boom() -> dict[str, int]:
        raise ValueError("bad json")

    with pytest.raises(ValueError):
        run_logged("digest", "2026-11-08", boom, log)
    line = RunLogLine.model_validate_json(log.read_text(encoding="utf-8"))
    assert line.status == "failure"
    assert line.error == "ValueError: bad json"
    assert line.counts == {}
