"""Archive job tests: move, idempotent re-run, missing digest fails."""

from pathlib import Path

import pytest

from backend.jobs.archive import TODAY_FILE, main
from backend.models import Digest
from backend.runlog import RunLogLine


def write_today(today_file: Path, date: str) -> None:
    digest = Digest(date=date, generated_at="now", stories=[])
    today_file.parent.mkdir(parents=True, exist_ok=True)
    today_file.write_text(digest.model_dump_json(), encoding="utf-8")


def test_archive_moves_today_to_dated_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log = tmp_path / "runs.jsonl"
    monkeypatch.setattr("backend.jobs.archive.TODAY_FILE", tmp_path / "digests" / "today.json")
    monkeypatch.setattr("backend.runlog.RUN_LOG", log)
    write_today(tmp_path / "digests" / "today.json", "2026-11-08")

    main()

    assert not (tmp_path / "digests" / "today.json").exists()
    archived = tmp_path / "digests" / "2026-11-08.json"
    assert Digest.model_validate_json(archived.read_text(encoding="utf-8")).date == "2026-11-08"
    line = RunLogLine.model_validate_json(log.read_text(encoding="utf-8"))
    assert line.job == "archive"
    assert line.status == "success"
    assert line.counts == {"archived": 1}


def test_archive_rerun_overwrites(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log = tmp_path / "runs.jsonl"
    monkeypatch.setattr("backend.jobs.archive.TODAY_FILE", tmp_path / "digests" / "today.json")
    monkeypatch.setattr("backend.runlog.RUN_LOG", log)
    write_today(tmp_path / "digests" / "today.json", "2026-11-08")
    main()
    write_today(tmp_path / "digests" / "today.json", "2026-11-08")
    main()

    assert log.read_text(encoding="utf-8").count("\n") == 2
    assert (tmp_path / "digests" / "2026-11-08.json").exists()


def test_archive_missing_digest_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log = tmp_path / "runs.jsonl"
    monkeypatch.setattr("backend.jobs.archive.TODAY_FILE", tmp_path / "digests" / "today.json")
    monkeypatch.setattr("backend.runlog.RUN_LOG", log)

    with pytest.raises(RuntimeError):
        main()

    line = RunLogLine.model_validate_json(log.read_text(encoding="utf-8"))
    assert line.status == "failure"
    assert "Run the digest job first" in (line.error or "")
