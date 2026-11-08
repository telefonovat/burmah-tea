# AGENTS.md — Burmahtea.com

Daily bilingual (Burmese/English) AI digest of trending news/politics posts from Burmese Facebook, plus a chat agent that answers questions about today's posts. CV/portfolio piece for LLM engineering roles.

## Stack

- **Frontend:** React + Vite + TypeScript (`frontend/`), pnpm, run from repo root: `pnpm run dev | build | preview`. Vite proxies `/api` → localhost:8000.
- **Backend:** Python 3.13 + uv workspace. FastAPI chat server + scraper in `backend/src/backend/` (`main.py`, `scraper.py`).
- **LLM:** `gemini-3.6-flash` via Google AI Studio, OpenAI-compatible client. Config in `backend/.env` (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `APIFY_TOKEN`).
- **Data:** Apify "Facebook Posts Scraper" on curated pages (`backend/pages.toml`), last-24h Myanmar Time (UTC+6:30) window.

## Commands

```bash
pnpm run dev                                      # frontend, localhost:5173
uv run --project backend uvicorn backend.main:app --port 8000   # API, localhost:8000
uv run --project backend python -m backend.scraper              # scrape → digest.today.test.json
```

## Conventions

- Keys only in `backend/.env` (gitignored). Never commit keys or `.env`.
- Chat answers only from the KB file (`frontend/src/data/digest.today.test.json`): cite source pages, admit gaps, never guess. Same rules for any new prompt.
- Burmese-first UI. System prompts must attribute claims ([reported] vs confirmed) — political content.
- `internal/` (gitignored) holds working notes and decisions; read `internal/decisions.md` before planning changes.

## Status (Nov 2026)

Chat MVP live on real scraped data. Next: summarisation step (scraped posts → digest page stories), trending signals (engagement velocity, reaction breakdown).
