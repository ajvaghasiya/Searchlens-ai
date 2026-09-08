from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CrawlResult, Website
from app.security import get_website_or_404
from app.services import heatmap as heatmap_service
from app.services import google_integrations
from app.services.insights import build_page_insights

router = APIRouter(prefix="/websites/{website_id}", tags=["insights"])


@router.get("/insights")
def page_insights(website_id: str, page_url: str = Query(...), db: Session = Depends(get_db)):
    """The single endpoint the 'Overview' dashboard tab calls: pulls the
    latest crawl, behaviour and search data for one URL and returns a short
    list of plain-language, prioritised recommendations."""
    website: Website = get_website_or_404(website_id, db)

    crawl_row = (
        db.query(CrawlResult)
        .filter(CrawlResult.website_id == website_id, CrawlResult.url == page_url)
        .order_by(CrawlResult.crawled_at.desc())
        .first()
    )
    crawl = None
    if crawl_row:
        crawl = {"issues": crawl_row.issues, "seo_score": crawl_row.seo_score}

    section_engagement = heatmap_service.build_section_engagement(db, website_id, page_url)
    cta_rate = heatmap_service.cta_click_rate(db, website_id, page_url)

    gsc_property = website.gsc_property or f"sc-domain:{website.domain}"
    gsc_rows = google_integrations.get_search_console_data(gsc_property, [page_url])
    gsc_row = gsc_rows[0] if gsc_rows else None

    insights = build_page_insights(crawl, section_engagement, cta_rate, gsc_row)

    return {
        "page_url": page_url,
        "seo_score": crawl["seo_score"] if crawl else None,
        "section_engagement": section_engagement,
        "cta_click_rate_pct": cta_rate,
        "search": gsc_row,
        "insights": insights,
    }
