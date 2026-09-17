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
- **Log-file Crawl Analysis**: ingest raw web server logs (Nginx/Apache style) 
  into a Python pandas pipeline (`backend/app/services/log_analysis.py`). Filter 
  to verified search-engine bots, segment requests by URL template, cross-reference 
  against Search Console indexation status to flag crawl budget waste (e.g. faceted URLs), 
  and surface response-code anomalies.
- **Automated Monitoring Pipeline**: a scheduling and orchestration layer 
  running on **n8n** triggers GA4/Search Console pulls, calls the crawl and 
  GEO/AEO scoring jobs, and routes the output. Monitoring runs unattended on 
  a recurring schedule instead of being kicked off by hand.
- **Behaviour analytics**: a single JS snippet (`sdk/tracker.js`, ~6KB, zero
  dependencies) collects clicks, scroll depth, section visibility and CTA
  interaction, then the dashboard renders it as click heatmaps and a
  per-content-section engagement view: what % of visitors actually reach
  the section targeting your keyword.
- **Search Console & GA4**: impressions, clicks, CTR, average position,
  sessions and conversions per page, with an automatic flag when CTR is
  underperforming the expected curve for a page's ranking position.
- **GEO / AEO visibility**: define a brand, competitors and a set of real
  buyer queries, run them against AI providers (ChatGPT, Perplexity), and track 
  mention rate, mention position, sentiment and cited source domains over time.
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

Instead, SearchLens AI does things they structurally can't or don't do. It sits directly on
your site via the tracker.js snippet to see real visitor behaviour. It ingests your raw 
server log files to analyze actual bot crawl behavior instead of just simulating a crawl. 
And it provides a customizable n8n automation layer so you can run all your monitoring 
pipelines unattended. It's a complementary engineering tool, not a replacement for a 
global keyword database.

| Feature | SearchLens AI | Ahrefs / SEMrush |
|---|---|---|
| **Core data source** | Crawls only the sites you point it at, server logs, and first-party SDK tracking | Continuously crawls the entire public web |
| **Backlink & Keyword Index** | None, no web-scale crawl or keyword search volume data | Massive global index, which is what you pay them for |
| **Log-File Crawl Analysis** | Yes, ingests Nginx/Apache logs to find wasted crawl budget and 5xx bottlenecks | No, they simulate crawls but cannot see how Googlebot actually interacts with your server |
| **On-site behaviour data** | Yes, tracks real clicks, scroll, and content engagement | None, no access to your site's visitor behaviour |
| **Automated Pipeline (CI/CD style)** | Yes, fully orchestrated via n8n for custom workflows and alerts | Proprietary scheduled emails and reports, but not an open automation pipeline |
| **AI/GEO visibility tracking** | Yes, built in, queries real AI providers directly | Adding some AI features, but not their core historical product |
| **Infrastructure & Pricing** | Free, self-hosted, fully Dockerized | Hosted SaaS, from roughly $129+/month |

## Google Analytics & Search Console Integration

SearchLens AI integrates directly with GA4 and Google Search Console to turn raw data into plain-language SEO recommendations. The logic sits in `backend/app/services/insights.py` and `google_integrations.py`.

### 1. Google Search Console (GSC) for SEO Opportunities
- **Why it's used:** GSC reveals how a page performs *before* the click (impressions, ranking position, and Click-Through Rate).
- **How it works:** SearchLens AI maintains a baseline curve of expected CTR per ranking position. It compares the real GSC data against this curve. If a page ranks at Position 5 with high impressions but its CTR is far below the expected baseline, the Insights Engine automatically flags it: *"The page ranks position 5 and gets meaningful impressions, but CTR is well below expected. Consider testing the title tag and meta description."*

### 2. Google Analytics (GA4) for Conversion Context
- **Why it's used:** GA4 reveals what happens *after* the click, tracking total sessions and conversions.
- **How it works:** This traffic data provides a baseline that is cross-referenced with our custom **Behaviour Tracking SDK**. If GA4 shows high traffic but low conversions, the SDK data explains exactly *why* users are dropping off (e.g., *"Only 40% of users scroll far enough to see the FAQ section, and only 12% interact with the primary Call To Action."*).

### Setup Instructions
The platform is designed to switch instantly from "Demo Mode" to live data:
1. Create a **Google Service Account** in Google Cloud and download the JSON key.
2. Set `GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/key.json` and `GA4_PROPERTY_ID=your_id` in your `.env` file.
3. Add the Service Account's email as a "Viewer" inside your real GSC and GA4 properties.
The project will instantly detect the credentials and begin making live API calls using the `google-api-python-client`.
## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, **pandas** (for log analysis) |
| Database | PostgreSQL (SQLite for zero-config local dev) |
| Crawler | `requests` + BeautifulSoup |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Chart.js |
| Tracking SDK | Vanilla JavaScript, no dependencies |
| AI / GEO | OpenAI (ChatGPT), Anthropic and Perplexity APIs (pluggable), with a demo provider fallback |
| Orchestration | **n8n** (Automated Monitoring Pipeline) |
| Infra | Docker, Docker Compose, **GitHub Actions (CI)** |

### Quick Start & Service Links

This project is **fully Docker-based**. You do not need Python or Node.js installed on your computer. Make sure you have Docker Desktop running.

**1. Start the platform (Development mode with hot-reloading):**
```bash
make dev
```

*(If you don't have `make` installed on Windows, you can just run: `docker compose -f docker-compose.dev.yml up -build`)*

**2. Access the Services:**
Once Docker is running, the platform is instantly available at the following links:

| Service | Local URL | Description |
|---|---|---|
| **User Dashboard** | [http://localhost:3000](http://localhost:3000) | The main Next.js interface. Start here to create a website and view reports. |
| **n8n Orchestrator** | [http://localhost:5678](http://localhost:5678) | The visual workflow builder. View and modify the background automation pipelines. |
| **FastAPI Backend** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger documentation for the Python API. |
| **Tracking SDK** | [http://localhost:8000/sdk/tracker.js](http://localhost:8000/sdk/tracker.js) | The raw JavaScript snippet to embed on client websites. |

**3. Generate Demo Data (Optional):**
To populate the dashboard with realistic user behaviour heatmaps and events, open a second terminal and run:
```bash
make seed
```

### Option B: Production Environment

If you want to run the optimized, statically built version without hot-reloading:
```bash
make up-prod
```

### Running the tests
To run the test suite inside the running Docker container:
```bash
make test
```

Covers the crawler against a real local HTTP server (good and bad pages),
the scoring logic, and a full API smoke test (create site → send tracking
events → read heatmap; create GEO config → run → read summary).

## Install the tracking snippet on a real site

```html
<script>
  window.SearchLensConfig = { siteKey: "slai_your_key_here" };
</script>
<!-- For local Docker testing, use http://localhost:8000/sdk/tracker.js -->
<script src="https://your-api-domain.com/sdk/tracker.js" defer></script>
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
