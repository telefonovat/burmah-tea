"""Archive job: move today.json to its dated archive file, resetting for the new day.

The digest's own date field decides the archive filename, so a late run still
archives to the right day. Re-runs overwrite the archive (same source, same
result). No git commit: everything under data/ stays local (internal/decisions.md).

Run: uv run --project backend python -m backend.jobs.archive
"""

from backend.config import DATA_DIR
from backend.models import Digest
from backend.runlog import run_logged
from backend.timeutil import today_mmt

TODAY_FILE = DATA_DIR / "digests" / "today.json"


def peek_day() -> str:
    """The day this run archives: the digest's own date, or today if unreadable."""
    if TODAY_FILE.exists():
        try:
            return Digest.model_validate_json(TODAY_FILE.read_text(encoding="utf-8")).date
        except Exception:
            return today_mmt().isoformat()
    return today_mmt().isoformat()


def main() -> None:
    def run() -> dict[str, int]:
        if not TODAY_FILE.exists():
            raise RuntimeError(f"No digest to archive: {TODAY_FILE} missing. Run the digest job first.")
        digest = Digest.model_validate_json(TODAY_FILE.read_text(encoding="utf-8"))
        target = TODAY_FILE.parent / f"{digest.date}.json"
        TODAY_FILE.replace(target)
        print(f"Archived {digest.date} digest -> {target}")
        return {"archived": 1}

    run_logged("archive", peek_day(), run)


if __name__ == "__main__":
    main()
