"""FastAPI backend: chat endpoint over the digest knowledge base.

KB = today's digest + latest archived digest + the source registry.
Answers only from the KB, cite sources with tier-appropriate hedging.
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

from backend.config import DATA_DIR, settings
from backend.models import Digest
from backend.sources import load_sources

app = FastAPI(title="burmahtea")

DIGESTS_DIR = DATA_DIR / "digests"
TODAY_FILE = DIGESTS_DIR / "today.json"


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


SYSTEM_PROMPT = """You are the assistant of a daily Burmese news digest. You answer only from the \
digest stories and the source registry below. If they do not answer the question, say so — do not guess.

Answering rules:
- If the question is about a specific topic, answer only that topic. Ignore the rest.
- If the question is a general news ask, give a brief digest of the popular and \
politically/economically important stories only — not every story.
- If the user asks for tea, gossip or drama ("tea", "အတင်း", "ပွဲ"), answer only with stories \
tagged "tea".
- Cite the source name for every claim.
- Hedge by tier: trustworthy — state as reported news; subpar — "according to X, a page of mixed \
reliability"; tabloid — "according to X, a tabloid page"; celebrity — "according to X's own page".
- Stories tagged "confirmed" are corroborated by multiple trustworthy outlets and can be presented \
as established. Stories tagged "tea" are unverified — never present them as fact.
- Be brief. Answer in the language the user writes in.

Source registry (name — tier):
{registry}

Digest stories:
{stories}"""


def load_kb() -> tuple[Digest, Digest | None]:
    """Today's digest (required) + the latest archived digest (optional)."""
    if not TODAY_FILE.exists():
        raise HTTPException(status_code=503, detail="no digest yet — run the digest job")
    today = Digest.model_validate_json(TODAY_FILE.read_text(encoding="utf-8"))
    archived: Digest | None = None
    archives = sorted(DIGESTS_DIR.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
    if archives:
        archived = Digest.model_validate_json(archives[-1].read_text(encoding="utf-8"))
    return today, archived


def build_system_prompt(today: Digest, archived: Digest | None) -> str:
    registry = "\n".join(f"{s.name} — {s.tier}" for s in load_sources())

    def stories_block(digest: Digest, label: str) -> str:
        lines = [f"[{label} — {digest.date}]"]
        for s in digest.stories:
            sources = ", ".join(f"{src.source_name} ({src.source_tier})" for src in s.sources)
            tags = ", ".join(s.tags) if s.tags else "none"
            lines.append(
                f"Story: {s.title}\nTags: {tags}\nSummary: {s.summary}\nSources: {sources}"
            )
        return "\n\n".join(lines)

    blocks = [stories_block(today, "TODAY")]
    if archived and archived.date != today.date:
        blocks.append(stories_block(archived, "PREVIOUS DAY"))
    return SYSTEM_PROMPT.format(registry=registry, stories="\n\n".join(blocks))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model": settings.llm_model}


@app.get("/api/digest/{view}")
def digest(view: str) -> dict:
    """Serve digest data. Pipeline writes data/, this is the single serving point."""
    if view not in ("today", "yesterday"):
        raise HTTPException(status_code=404, detail="view must be today or yesterday")
    path: Path
    if view == "today":
        path = TODAY_FILE
    else:
        archives = sorted(DIGESTS_DIR.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
        if not archives:
            raise HTTPException(status_code=404, detail="no archived digest yet")
        path = archives[-1]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"no digest for {view}")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    today, archived = load_kb()
    system = build_system_prompt(today, archived)

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    completion = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            *[{"role": m.role, "content": m.content} for m in req.messages],
        ],
    )
    answer = completion.choices[0].message.content or ""

    kb_sources = {src.source_name for s in today.stories for src in s.sources}
    if archived:
        kb_sources |= {src.source_name for s in archived.stories for src in s.sources}
    sources = sorted({name for name in kb_sources if name in answer})
    return ChatResponse(answer=answer, sources=sources)


# Serve the built frontend (frontend/dist) from the same port as the API.
# Mounted last so /api routes win; absent in local dev where Vite serves the app.
DIST_DIR = Path(__file__).parents[3] / "frontend" / "dist"
if DIST_DIR.is_dir():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")
