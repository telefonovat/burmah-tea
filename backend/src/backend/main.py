"""FastAPI backend: minimal chat endpoint over the today digest knowledge base."""

import json
from pathlib import Path

from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute so the env file loads no matter where uvicorn is started from.
ENV_FILE = Path(__file__).parents[2] / ".env"
DATA_FILE = Path(__file__).parents[3] / "frontend" / "src" / "data" / "digest.today.json"


class Settings(BaseSettings):
    """LLM config, loaded from backend/.env."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    llm_api_key: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-3.8-flash"


settings = Settings()
app = FastAPI(title="burmahtea")


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


SYSTEM_PROMPT = """You are a Burmese news digest assistant. Answer only from the posts below.
Cite the source page name for every claim. If the posts do not answer the question, say so — do not guess.
Answer in the language the user writes in.

Posts:
{posts}"""


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model": settings.llm_model}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    posts = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    posts_text = "\n\n".join(
        f"Title: {p['title']}\nSummary: {p['summary']}\nSource: {p['page_name']}"
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
