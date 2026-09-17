# Developer Onboarding Guide

Welcome to the **SearchLens AI** repository! This guide will help you get the project running locally and understand the architecture so you can start contributing quickly.

---

## 🏗 Architecture Overview

SearchLens AI is a decoupled, microservices-based application running fully in Docker.

1. **Frontend (`/frontend`)**: Next.js 14, Tailwind CSS, React.
2. **Backend (`/backend`)**: Python (FastAPI), SQLAlchemy. Exposes the core REST API and handles data processing (crawling, logs, LLM calls).
3. **Database**: PostgreSQL (via Docker) with an SQLite fallback for rapid testing.
4. **Tracking SDK (`/sdk`)**: A vanilla JavaScript snippet designed to be embedded on client websites to track user behaviour.
5. **Orchestration**: **n8n** acts as the central workflow automation engine.

---

## 🛠 Prerequisites

Because the entire stack is containerized, you **do not** need Python or Node.js installed locally. You only need:
- **Git**
- **Docker** and **Docker Compose** (Docker Desktop is recommended for Windows/Mac)

*(Optional but recommended): `make` is used for shortcut commands. If you are on Windows and don't have `make`, you can run the raw Docker commands provided below.*

---

## 🚀 Step-by-Step Setup

### 1. Clone & Configure Environment
First, clone the repository and set up your environment variables.
```bash
git clone https://github.com/your-username/searchlens-ai.git
cd searchlens-ai
cp .env.example .env
```
*Note: The project is designed to run perfectly in "Demo Mode" without any real API keys. You can add Google Service Account JSONs or OpenAI keys later to pull real data.*

### 2. Start the Development Environment
Run the following command to spin up the entire stack with hot-reloading enabled:
```bash
make dev
```
*(If you don't have `make` installed: `docker compose -f docker-compose.dev.yml up --build`)*

The first build will take a few minutes as it pulls the Node and Python images.

### 3. Verify the Services are Running
Once the containers are up, you can access the services at:
- **User Dashboard (Next.js):** [http://localhost:3000](http://localhost:3000)
- **API Documentation (FastAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **n8n Workflow Builder:** [http://localhost:5678](http://localhost:5678)

### 4. Seed the Database (Optional but highly recommended)
To populate the database with realistic demo data (websites, mock behaviour heatmaps, and past crawls), open a **new terminal tab** and run:
```bash
make seed
```
*(Without `make`: `docker compose -f docker-compose.dev.yml exec backend python -m app.scripts.seed_db`)*

---

## 📂 Project Structure

Here is where you'll find the core logic:

```text
searchlens-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── models.py               # SQLAlchemy Database schemas
│   │   ├── routers/                # API Endpoints (e.g., websites.py)
│   │   └── services/               # Core business logic (crawler, scoring, LLM, Google APIs)
│   └── requirements.txt
├── frontend/
│   ├── app/                        # Next.js App Router (Pages & Layouts)
│   ├── components/                 # Reusable UI components
│   └── lib/                        # API client and utilities
├── sdk/
│   └── tracker.js                  # The raw JavaScript snippet for client websites
├── workflows/
│   └── seo_monitoring.json         # The exported n8n orchestration pipeline
├── docker-compose.yml              # Production Docker config
└── docker-compose.dev.yml          # Development Docker config (volume mounts)
```

---

## 🔧 Workflow Automation (n8n)

When a user creates a new website in the dashboard, the backend triggers an **n8n webhook** to run the orchestration pipeline (crawling, GEO checks, GA4 syncing). 

If you are modifying the pipeline:
1. Open n8n at [http://localhost:5678](http://localhost:5678).
2. Modify the workflow visually.
3. If you want to commit your changes, export the workflow to `workflows/seo_monitoring.json`.

---

## 🐛 Common Troubleshooting

**1. "Cannot POST /webhook/run-monitoring" (n8n Error)**
If you see this error in the dashboard logs, it means the n8n workflow is currently deactivated. 
- Open [http://localhost:5678](http://localhost:5678)
- Open the "SearchLens SEO Monitoring Pipeline"
- Ensure the toggle in the top right is set to **Active**.

**2. Frontend UI changes aren't appearing (Windows Users)**
Docker volume mounts on Windows can occasionally drop file-system events, causing Next.js hot-reloading to freeze. If your UI changes aren't updating in the browser, restart the frontend container:
```bash
docker compose -f docker-compose.dev.yml restart frontend
```

**3. Database Migrations**
We currently use `Base.metadata.create_all(bind=engine)` in `main.py` which automatically creates tables. If you add a new model to `models.py`, simply restart the backend container:
```bash
docker compose -f docker-compose.dev.yml restart backend
```
