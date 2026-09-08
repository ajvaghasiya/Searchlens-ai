# Architecture

## Overview

SearchLens AI is a monorepo with three parts:

```
searchlens-ai/
├── backend/    FastAPI service: crawler, behaviour aggregation, GSC/GA4, GEO
├── sdk/        tracker.js, the client-side snippet installed on tracked sites
├── frontend/   Next.js dashboard
└── docs/       this folder
```

Data flows like this:

```
Tracked website
  └── tracker.js (SDK) ──POST /api/v1/track──► FastAPI ──► Postgres/SQLite
                                                    ▲
Search Console / GA4 ──service account──►──────────┤
                                                    │
AI providers (OpenAI/Anthropic/Perplexity) ◄───────┤ GEO module
                                                    │
                                              Next.js dashboard
                                              (reads via /api/v1/*)
```

## Module boundaries

| Module | Backend location | What it owns |
|---|---|---|
| Technical SEO | `app/services/crawler.py`, `app/services/scoring.py`, `app/routers/crawl.py` | Fetching and analysing pages, the SEO Health Score |
| Behaviour | `app/services/heatmap.py`, `app/routers/track.py`, `sdk/tracker.js` | Raw event ingestion, click/scroll/section aggregation |
| Search analytics | `app/services/google_integrations.py`, `app/routers/seo.py` | GSC/GA4 data, with demo fallback |
| GEO / AEO | `app/services/geo.py`, `app/routers/geo.py` | AI provider queries, mention/citation analysis |
| Insights | `app/services/insights.py`, `app/routers/insights.py` | Combines all four into plain-language recommendations |

Each module's demo-mode fallback lives next to its real implementation in
the same file (`google_integrations.py`, `geo.py`), specifically so it is
easy to see exactly which numbers are real API data and which are seeded
synthetic data when reading the code.

## Why these tradeoffs

**SQLite by default, Postgres via docker-compose.** A contributor should be
able to `pip install -r requirements.txt && uvicorn app.main:app` and have
a working API in under a minute. `docker-compose up` gets the full stack
including Postgres for anything closer to production.

**API-key auth instead of full user accounts.** Each website gets a random
key at creation time (`Website.api_key`). It doubles as the "site key" used
by the public `/track` endpoint. This is enough to demo and self-host the
product. Multi-user accounts with proper login and roles are the natural
next step, see Roadmap below.

**Synchronous crawling.** `POST /websites/{id}/crawl` crawls URLs inline
and returns when done. Fine for a handful of pages or a demo; a real
multi-page site audit should move to a background worker (Celery/RQ with
Redis, or FastAPI `BackgroundTasks` for something lighter) so the request
doesn't block.

**Rule-based insights, not an LLM call.** `app/services/insights.py` encodes
real SEO heuristics (the expected-CTR-by-position curve, an engagement
threshold, a thin-content limit) as plain Python. It's deterministic, free
to run, and easy to explain line by line. An LLM-narrated version of the
same underlying signals is a good follow-up, not a replacement.

## Roadmap

Roughly in priority order:

1. **Background crawling** for whole-site audits (Celery/RQ + Redis), plus
   sitemap.xml discovery instead of link-following only.
2. **Alembic migrations** to replace the current `create_all()` bootstrap,
   needed once the schema needs to evolve without dropping data.
3. **Proper OAuth for Search Console** as an alternative to the service
   account flow, for users who don't want to add a service account as a
   Search Console user.
4. **JS rendering in the crawler** (Playwright) for JS-heavy sites, current
   crawler only sees server-rendered HTML.
5. **Multi-user accounts** with JWT auth and per-user site ownership.
6. **Scheduled crawls and GEO runs** instead of manual triggers.
7. **LLM-narrated insights** as an optional richer layer on top of the
   existing rule-based recommendations.
