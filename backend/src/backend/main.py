"""FastAPI backend: chat endpoint over the digest knowledge base."""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API keys and model config, loaded from backend/.env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    dashscope_api_key: str = ""
    qwen_model: str = "qwen3.6-27b"


settings = Settings()
app = FastAPI(title="burmahtea")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parents[3] / "frontend" / "src" / "data"


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


def load_knowledge_base() -> list[dict]:
    """Load today's and yesterday's posts as the agent's knowledge base."""
    posts: list[dict] = []
    for name in ("digest.today.json", "digest.yesterday.json"):
        path = DATA_DIR / name
        if path.exists():
            posts.extend(json.loads(path.read_text(encoding="utf-8")))
    return posts


SYSTEM_PROMPT = """You are a Burmese news digest assistant. Answer only from the posts below.
Cite the source page name for every claim. If the posts do not answer the question, say so — do not guess.
Answer in the language the user writes in (Burmese or English).

Posts:
{posts}"""


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model": settings.qwen_model}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    posts = load_knowledge_base()
    posts_text = "\n\n".join(
        f"Title: {p['title']}\nSummary: {p['summary']}\nSource: {p['page_name']}"
        for p in posts
    )
    system = SYSTEM_PROMPT.format(posts=posts_text)

    if not settings.dashscope_api_key:
        return ChatResponse(
            answer="API key မထည့်ရှိပါ။ backend/.env တွင် DASHSCOPE_API_KEY ထည့်ပါ။",
            sources=[],
        )

    client = OpenAI(
        api_key=settings.dashscope_api_key,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": system},
            *[{"role": m.role, "content": m.content} for m in req.messages],
        ],
    )
    answer = completion.choices[0].message.content or ""

    sources = sorted({p["page_name"] for p in posts if p["page_name"] in answer})
    return ChatResponse(answer=answer, sources=sources)
