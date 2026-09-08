from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CrawlResult
from app.schemas import CrawlRequest, CrawlResultOut
from app.security import get_website_or_404
from app.services.crawler import crawl_page
from app.services.scoring import score_page

router = APIRouter(prefix="/websites/{website_id}/crawl", tags=["technical-seo"])


@router.post("", response_model=list[CrawlResultOut])
def run_crawl(website_id: str, payload: CrawlRequest, db: Session = Depends(get_db)):
    """Synchronous crawl of the given URLs. For anything beyond a handful of
    pages this should move to a background worker (see docs/architecture.md),
    but keeping it synchronous keeps the demo dead simple to run and reason
    about."""
    get_website_or_404(website_id, db)

    saved: list[CrawlResult] = []
    for url in payload.urls:
        page = crawl_page(url)
        score = score_page(page)
        row = CrawlResult(
            website_id=website_id,
            url=page.url,
            status_code=page.status_code,
            response_time_ms=page.response_time_ms,
            title=page.title,
            title_length=page.title_length,
            meta_description=page.meta_description,
            meta_description_length=page.meta_description_length,
            h1_count=page.h1_count,
            h1_text=page.h1_text,
            canonical_url=page.canonical_url,
            robots_meta=page.robots_meta,
            word_count=page.word_count,
            internal_links=page.internal_links,
            external_links=page.external_links,
            images_missing_alt=page.images_missing_alt,
            has_structured_data=page.has_structured_data,
            structured_data_types=page.structured_data_types,
            issues=page.issues,
            seo_score=score,
        )
        db.add(row)
        saved.append(row)

    db.commit()
    for row in saved:
        db.refresh(row)
    return saved


@router.get("/latest", response_model=list[CrawlResultOut])
def latest_crawl(website_id: str, db: Session = Depends(get_db)):
    get_website_or_404(website_id, db)
    return (
        db.query(CrawlResult)
        .filter(CrawlResult.website_id == website_id)
        .order_by(CrawlResult.crawled_at.desc())
        .limit(50)
        .all()
    )
