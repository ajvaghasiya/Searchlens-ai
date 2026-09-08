from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Website, BehaviorEvent
from app.schemas import TrackBatch
from app.security import get_website_or_404
from app.services import heatmap as heatmap_service

router = APIRouter(tags=["behaviour"])


@router.post("/track")
def ingest_events(payload: TrackBatch, db: Session = Depends(get_db)):
    """Public endpoint hit by tracker.js. Authenticated by the site key that
    ships in the public snippet, not by the private API key used elsewhere,
    since this call has to be made from anonymous browsers."""
    website = db.query(Website).filter(Website.api_key == payload.site_key).first()
    if not website:
        raise HTTPException(status_code=401, detail="Unknown site key")

    rows = [
        BehaviorEvent(
            website_id=website.id,
            session_id=e.session_id,
            page_url=e.page_url,
            event_type=e.event_type,
            x_pct=e.x_pct,
            y_pct=e.y_pct,
            scroll_depth_pct=e.scroll_depth_pct,
            section_id=e.section_id,
            duration_ms=e.duration_ms,
            device_type=e.device_type,
            meta=e.meta,
        )
        for e in payload.events
    ]
    db.bulk_save_objects(rows)
    db.commit()
    return {"accepted": len(rows)}


@router.get("/websites/{website_id}/heatmap")
def get_heatmap(website_id: str, page_url: str, db: Session = Depends(get_db)):
    get_website_or_404(website_id, db)
    return {
        "click_grid": heatmap_service.build_click_grid(db, website_id, page_url),
        "scroll": heatmap_service.build_scroll_curve(db, website_id, page_url),
        "section_engagement": heatmap_service.build_section_engagement(db, website_id, page_url),
        "cta_click_rate_pct": heatmap_service.cta_click_rate(db, website_id, page_url),
    }
