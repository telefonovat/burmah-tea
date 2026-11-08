"""Load and validate the curated source registry (data/sources.yaml)."""

import yaml

from backend.config import DATA_DIR
from backend.models import Source

SOURCES_FILE = DATA_DIR / "sources.yaml"


def load_sources() -> list[Source]:
    with SOURCES_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    sources = [Source.model_validate(s) for s in data["sources"]]
    ids = [s.id for s in sources]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate source ids in {SOURCES_FILE}")
    return sources
