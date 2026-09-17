# SearchLens AI: Case Study & Architecture Overview

## The Elevator Pitch
**SearchLens AI** is an end-to-end Organic Search & AI Visibility Intelligence Platform. It replaces four distinct marketing tools by unifying them into a single, automated dashboard:
1. A **Technical SEO Crawler**
2. A custom **On-Site Behaviour Analytics SDK**
3. **Google Analytics & Search Console** integration
4. An **AI Search Visibility (GEO/AEO)** tracker

Instead of forcing users to export CSVs and manually cross-reference data, the platform uses an automated orchestration pipeline to ingest all four data streams and output a single, prioritized list of plain-language SEO recommendations per page.

---

## 🏗 System Architecture & Tech Stack

The platform is designed as a decoupled, microservices architecture, fully containerized using Docker.

- **Frontend:** Next.js 14 (React), TypeScript, Tailwind CSS, Chart.js.
- **Backend API:** Python, FastAPI, SQLAlchemy.
- **Database:** PostgreSQL (with SQLite fallback for zero-config local development).
- **Data Engineering:** `pandas` for ingesting and processing raw Nginx/Apache log files.
- **Orchestration:** **n8n** (Automated workflow orchestration).
- **AI Integrations:** OpenAI, Anthropic, and Perplexity APIs.

---

## ⚙️ Core Modules Explained

### 1. Technical SEO & Log File Crawler
Instead of relying on third-party SaaS crawlers, the Python backend uses `requests` and `BeautifulSoup` to crawl pages exactly how Googlebot does.
- **What it checks:** Titles, meta descriptions, missing alt text, response codes, canonicals, and H1s.
- **Log File Analysis:** Ingests raw server logs to detect wasted crawl budget, identifying bot traffic and 5xx bottlenecks that standard crawlers miss.

### 2. Custom Behaviour Tracking SDK
A lightweight (~6KB), zero-dependency vanilla JavaScript SDK (`tracker.js`) installed on the client’s website.
- **What it does:** Tracks exact user interactions including click heatmaps, scroll depth, section visibility, and Call-to-Action (CTA) conversions.
- **The Value:** Allows the platform to answer *why* a page isn't converting, instead of just reporting that traffic dropped. 

### 3. Google Search Console & GA4 Integration
Directly integrates via the `google-api-python-client` (Service Account Auth).
- **Search Console (Pre-Click):** Maps a page's actual Click-Through Rate (CTR) against an algorithmic baseline curve for its ranking position. If CTR underperforms, the system flags a title/meta tag optimization opportunity.
- **GA4 (Post-Click):** Evaluates total traffic vs. conversions, passing the context to the Behaviour SDK to explain the drop-off.

### 4. Generative Engine Optimization (GEO/AEO)
Traditional SEO focuses on Google. This module focuses on Large Language Models.
- **How it works:** Users define their Brand, Competitors, and target Queries. The backend directly queries ChatGPT and Perplexity APIs to measure how often the brand is recommended, calculating a proprietary "AI Visibility Score".

### 5. Automated Orchestration (n8n)
The "Magic Onboarding" and background scheduling layer.
- **Why n8n?:** Instead of hardcoding background jobs (e.g., Celery/Redis), the platform uses n8n. This empowers non-technical marketing teams to visually program the pipeline. 
- **The Flow:** A user adds a domain in the Next.js UI → FastAPI receives it → triggers an n8n webhook → n8n orchestrates the crawler, GEO checks, and GA4 pulls sequentially → n8n formats the report and posts it back to the dashboard.

---

## 💡 The Value Proposition (How it differs from Ahrefs/SEMrush)

In an interview, if asked *"Why build this when Ahrefs exists?"*:

1. **First-Party Data vs. Third-Party Estimates:** Ahrefs simulates crawls and relies on global keyword databases. SearchLens AI sits directly on the server (via log files) and the client browser (via the SDK) to report **actual user and bot behavior**.
2. **Actionable Synthesis:** Standard tools give you hundreds of disconnected metrics. SearchLens combines GA4 traffic, SDK scroll-depth, and GSC rankings to say: *"Page X gets high impressions but low CTR. Of the users who do click, 60% never scroll to the pricing table."*
3. **No-Code Automation:** Standard tools trap you in their reporting UI. SearchLens exposes a programmable n8n pipeline, allowing agencies to automatically route critical SEO drops to Slack or Jira without writing any code.
