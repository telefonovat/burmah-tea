# Burmahtea.com

Daily bilingual (Burmese/English) AI-powered digest of trending news and gossip from Burma Facebook

**Live:** https://burmahtea.duckdns.org

A lot of drama occurs on Burman-speaking Facebook. As I do not often use social media, I miss out on the tea. Burmahtea delivers a nicely curated digest of stories of the last 24 hours.

<!-- One or two sentences on why this exists: tea shops are where Myanmar reads
     the news; this is the digital version. Recruiters read only the first
     paragraph — make it count. -->

## How it works

```
Apify (12 curated pages, tiered by trust)
        │
        ▼  fetch job (daily, idempotent upsert)
SQLite post store (data/posts.db)
        │
        ▼  digest job (one LLM call: cluster + bilingual summaries + gossip judgment)
digests/today.json ── mechanical tags: confirmed (2+ trustworthy sources),
        │              popular (top decile of the day's engagement)
        ▼
FastAPI ──── serves digest + /api/chat (answers only from the digest,
        │    cites sources, hedges by trust tier)
        ▼
React + Vite (Burmese-first UI, မ/EN toggle, tea-house theme)
```

<!-- The design philosophy line, worth keeping somewhere:
     "The LLM decides what a story is; arithmetic decides how true or popular." -->

## Pipeline

Three independent CLI jobs, one shared JSONL run log (`data/logs/runs.jsonl`):

| Job     | What                                                  | When (MMT) |
|---------|-------------------------------------------------------|------------|
| fetch   | Apify scrape of last 24h → upsert into SQLite          | 22:15      |
| digest  | recompute the day's digest from scratch, one LLM call  | 22:45      |
| archive | move today.json → dated archive                        | 00:15      |

Tags: `tea` is LLM judgment (gossip/rumor content); `confirmed` and `popular` are
mechanical rules — the LLM never decides how true or popular a story is.

## Stack

Python 3.13 (pydantic v2, FastAPI, uv) · React 19 + Vite + TypeScript · SQLite ·
Apify Facebook Posts Scraper · Gemini Flash via OpenAI-compatible API ·
Caddy + cron on a DigitalOcean droplet

## Success metric

Posts/day stable for two weeks, verifiable from the run log.
<!-- Update once the two weeks are in: "Ran N days, M posts, zero missed runs." -->

## Cost

~$15/month: Apify (~$0.50/day per fetch) + LLM pennies per digest (TBA)
<!-- Replace with real numbers — cost-conscious design is part of the pitch. -->

## Development

```bash
pnpm run dev                                                   # frontend :5173
uv run --project backend uvicorn backend.main:app --port 8000  # API :8000
uv run --project backend python -m backend.jobs.fetch --no-fetch  # fixture mode, no Apify spend
uv run --project backend pytest backend/tests                  # 26 tests
```

## What's next
Please note that the roadmap may change as development matures.

- [ ] Healthchecks
- [ ] Metrics renderer
- [ ] Better clustering of stories
- [ ] E2E tests
- [ ] Smarter Chat Agent
    + [ ] Memory beyond one day
    + [ ] Knowledge of local Burmese figures(Entity glossary)
- [ ] A more scientific tiering of sources with transparent methodology
- [ ] Automate deployment and testing infrastructure

<!-- Honest backlog: Healthchecks dead-man's-switch, metrics renderer, better
     clustering, Playwright e2e. Shows you think in iterations. -->
