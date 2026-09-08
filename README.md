# SearchLens AI

**Organic Search & AI Visibility Intelligence Platform**

SearchLens AI connects four things that are usually four separate tools:
a technical SEO crawler, on-site behaviour analytics, Search Console/GA4
reporting, and AI search (GEO/AEO) visibility tracking, then turns all of
it into a short list of plain-language recommendations per page.

It's built to be run and read end to end: every module works with zero
external accounts in demo mode, and switches to real data the moment you
add credentials.

```
Technical SEO  +  User Behaviour  +  Search Analytics  +  AI Search Visibility
        \_______________________|_______________________/
                                 |
                    one SEO Health Score, one
                    set of prioritised insights
```

## Why this exists

I built this to go deeper on technical SEO, behaviour analytics and GEO/AEO
than a CV bullet point can show, and because building the crawler, the
tracking SDK and the AI-visibility engine myself was a better way to
actually understand how they work than reading about them. It also gave me
a single project that maps to Technical SEO, SEO Engineering, Website &
Conversion, and GEO/Digital Trust roles instead of three unrelated demos.



## Status

This is an active portfolio project, not a finished commercial product.
Being specific about what's real:

| | Status |
|---|---|
| Technical SEO crawler | **Fully working.** Real HTTP requests, real HTML parsing, real scoring. Tested. |
| Behaviour tracking SDK | **Fully working.** Real client-side event capture, real ingestion API. |
| Behaviour aggregation (heatmaps, engagement) | **Fully working**, computed from whatever events you send it. |
| Search Console / GA4 | **Real integration code included** (service account auth). Falls back to seeded demo data with no credentials, so the dashboard is always explorable. |
| GEO / AEO | **Real integration code included** for OpenAI, Anthropic and Perplexity. Falls back to a seeded demo provider with no keys. |
| Insights engine | **Fully working**, rule-based (not an LLM call, see `docs/architecture.md` for why). |
| Multi-user accounts, billing, scheduled crawls | **Not built yet.** See the Roadmap in `docs/architecture.md`. |

Full breakdown of what's real vs demo-mode fallback is in
[`docs/architecture.md`](docs/architecture.md).

## Features

- **Technical SEO crawler**: titles, meta descriptions, headings, canonicals,
  robots directives, structured data, internal/external links, missing alt
  text, thin content, response time. Screaming-Frog-style checks, with a
  documented 0-100 scoring formula (`backend/app/services/scoring.py`).
- **Behaviour analytics**: a single JS snippet (`sdk/tracker.js`, ~6KB, zero
  dependencies) collects clicks, scroll depth, section visibility and CTA
  interaction, then the dashboard renders it as click heatmaps and a
  per-content-section engagement view: what % of visitors actually reach
  the section targeting your keyword.
- **Search Console & GA4**: impressions, clicks, CTR, average position,
  sessions and conversions per page, with an automatic flag when CTR is
  underperforming the expected curve for a page's ranking position.
- **GEO / AEO visibility**: define a brand, competitors and a set of real
  buyer queries, run them against AI providers, and track mention rate,
  mention position, sentiment and cited source domains over time.
- **Cross-module insights**: one endpoint combines all of the above into
  the kind of recommendation a human analyst would write, e.g. *"The page
  ranks position 7.2 and gets solid impressions, but CTR is well below
  expected for that position, test the title and meta description."*

See [`docs/api-reference.md`](docs/api-reference.md) for every endpoint and
[`docs/geo-methodology.md`](docs/geo-methodology.md) for exactly how the
AI visibility score is calculated.

## How this is different from Ahrefs / SEMrush

Worth being upfront about this: SearchLens AI is not a competitor to Ahrefs
or SEMrush, and isn't trying to be. Their core value is a backlink and
keyword index built by continuously crawling the entire public web, which
is expensive infrastructure this project doesn't attempt to replicate.
SearchLens AI does something they structurally can't: it sits directly on
one site via the tracker.js snippet and sees real visitor behaviour, then
ties that to the technical crawl and search performance data for the same
page. Complementary tool, not a replacement.

| | SearchLens AI | Ahrefs | SEMrush |
|---|---|---|---|
| Core data source | Crawls only the sites you point it at, plus first-party tracking installed on that site | Continuously crawls the entire public web | Continuously crawls the entire public web |
| Backlink index | None, no web-scale crawl of external links | Trillions of tracked links, updated constantly | Large index, similar scale to Ahrefs |
| Keyword volume/difficulty database | None | Yes, across many countries and search engines | Yes, plus PPC and advertising data |
| On-site behaviour data (clicks, scroll, engagement) | Yes, this is the core differentiator | None, no access to your site's visitor behaviour | None |
| AI/GEO visibility tracking | Yes, built in, queries real AI providers directly | Adding some features, not their core product | Adding some features, not their core product |
| Infrastructure needed | A server you run yourself | None, fully hosted SaaS | None, fully hosted SaaS |
| Pricing | Free, self-hosted, open source | From roughly $129/month | From roughly $139/month |

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL (SQLite for zero-config local dev) |
| Crawler | `requests` + BeautifulSoup |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Chart.js |
| Tracking SDK | Vanilla JavaScript, no dependencies |
| AI / GEO | OpenAI, Anthropic and Perplexity APIs (pluggable), with a demo provider fallback |
| Infra | Docker, Docker Compose, GitHub Actions |

## Quick start

### Option A: Docker Compose (full stack, closest to production)

```bash
git clone https://github.com/your-username/searchlens-ai.git
cd searchlens-ai
cp .env.example .env      # optional: add real credentials, or leave blank for demo mode
docker compose up --build
```

- API: http://localhost:8000 (interactive docs at `/docs`)
- Dashboard: http://localhost:3000

### Option B: Run locally without Docker

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

This uses SQLite by default (`DATABASE_URL` in `.env`), no database
install required. Optionally seed some demo behaviour data:

```bash
python -m scripts.seed_demo_data
```

**Frontend**, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000/dashboard, create a website, and start crawling.

### Running the tests

```bash
cd backend
python -m pytest tests/ -v
```

Covers the crawler against a real local HTTP server (good and bad pages),
the scoring logic, and a full API smoke test (create site → send tracking
events → read heatmap; create GEO config → run → read summary).

## Install the tracking snippet on a real site

```html
<script>
  window.SearchLensConfig = { siteKey: "slai_your_key_here" };
</script>
<script src="https://your-api-domain.com/tracker.js" defer></script>
```

Mark the content sections and CTA you want engagement data for:

```html
<section data-slai-section="pricing">...</section>
<a href="/signup" data-slai-cta="primary-cta">Start free trial</a>
```

Full SDK docs: [`sdk/README.md`](sdk/README.md). Privacy/GDPR notes:
[`docs/privacy.md`](docs/privacy.md).

## Project layout

```
searchlens-ai/
├── backend/          FastAPI app, crawler, GEO engine, tests
├── sdk/               tracker.js and its docs
├── frontend/          Next.js dashboard
├── docs/               architecture, API reference, GEO methodology, privacy
├── docker-compose.yml
└── .env.example
```

## License

MIT, see [`LICENSE`](LICENSE).
