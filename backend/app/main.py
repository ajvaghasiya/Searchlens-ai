from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import websites, crawl, track, seo, geo, insights

settings = get_settings()

# For a portfolio / demo project, creating tables on startup keeps setup to
# "docker compose up" with no separate migration step. A production fork
# should replace this with Alembic migrations (scaffold noted in
# docs/architecture.md).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Organic search and AI visibility intelligence: technical SEO, "
                 "on-site behaviour, Search Console/GA4 analytics and GEO/AEO "
                 "in one API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websites.router, prefix=settings.API_V1_PREFIX)
app.include_router(crawl.router, prefix=settings.API_V1_PREFIX)
app.include_router(track.router, prefix=settings.API_V1_PREFIX)
app.include_router(seo.router, prefix=settings.API_V1_PREFIX)
app.include_router(geo.router, prefix=settings.API_V1_PREFIX)
app.include_router(insights.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
