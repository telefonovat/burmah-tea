"""FastAPI backend: minimal chat endpoint over the today digest knowledge base."""

import json

from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from backend.config import DATA_DIR, settings

app = FastAPI(title="burmahtea")


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


# Scraped posts from the pipeline (scraper.py output). Chat answers from these.
KB_FILE = DATA_DIR / "digest.today.test.json"
# Cap each post's text so a few long posts can't crowd out the rest of the KB.
MAX_POST_CHARS = 3000

SYSTEM_PROMPT = """You are a Burmese news digest assistant. Answer only from the posts below.
Cite the source page name for every claim. If the posts do not answer the question, say so — do not guess.
Be brief and succint.
Answer in the language the user writes in.

Posts:
{posts}"""


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model": settings.llm_model}


@app.get("/api/digest/{view}")
def digest(view: str) -> list[dict]:
    """Serve digest data. Pipeline writes data/, this is the single serving point."""
    if view not in ("today", "yesterday"):
        raise HTTPException(status_code=404, detail="view must be today or yesterday")
    path = DATA_DIR / f"digest.{view}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"no digest for {view}")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    posts = json.loads(KB_FILE.read_text(encoding="utf-8"))
    posts_text = "\n\n".join(
        f"Text: {p['text'][:MAX_POST_CHARS]}\nSource: {p['page_name']}"
        for p in posts
    )
    system = SYSTEM_PROMPT.format(posts=posts_text)

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

    sources = sorted({p["page_name"] for p in posts if p["page_name"] in answer})
    return ChatResponse(answer=answer, sources=sources)
