from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CrawlResult
from app.security import get_website_or_404
from app.services import google_integrations

router = APIRouter(prefix="/websites/{website_id}", tags=["search-analytics"])


@router.get("/search-console")
def search_console_data(website_id: str, db: Session = Depends(get_db)):
    website = get_website_or_404(website_id, db)
    pages = _crawled_urls(db, website_id)
    gsc_property = website.gsc_property or f"sc-domain:{website.domain}"
    return google_integrations.get_search_console_data(gsc_property, pages)


@router.get("/ga4")
def ga4_data(website_id: str, db: Session = Depends(get_db)):
    get_website_or_404(website_id, db)
    pages = _crawled_urls(db, website_id)
    return google_integrations.get_ga4_data(pages)


def _crawled_urls(db: Session, website_id: str, limit: int = 25) -> list[str]:
    rows = (
        db.query(CrawlResult.url)
        .filter(CrawlResult.website_id == website_id)
        .distinct()
        .limit(limit)
        .all()
    )
    return [r[0] for r in rows]
