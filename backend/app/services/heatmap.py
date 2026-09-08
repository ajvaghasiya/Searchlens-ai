"""
Aggregation logic for the behaviour analytics module. Raw events collected
by tracker.js (see /sdk/tracker.js) are stored one row per event. These
functions turn that raw table into the shapes the dashboard actually
renders: a click-density grid and a per-content-section view rate, which is
the piece that makes this an SEO tool rather than a generic heatmap clone.
"""
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import BehaviorEvent

GRID_SIZE = 20  # 20x20 buckets across the normalised 0-100% page surface


def build_click_grid(db: Session, website_id: str, page_url: str) -> list[dict]:
    events = (
        db.query(BehaviorEvent)
        .filter(
            BehaviorEvent.website_id == website_id,
            BehaviorEvent.page_url == page_url,
            BehaviorEvent.event_type == "click",
        )
        .all()
    )

    grid: dict[tuple[int, int], int] = defaultdict(int)
    bucket_size = 100 / GRID_SIZE

    for event in events:
        if event.x_pct is None or event.y_pct is None:
            continue
        x_bucket = min(GRID_SIZE - 1, int(event.x_pct // bucket_size))
        y_bucket = min(GRID_SIZE - 1, int(event.y_pct // bucket_size))
        grid[(x_bucket, y_bucket)] += 1

    return [
        {"x_bucket": x, "y_bucket": y, "count": count}
        for (x, y), count in sorted(grid.items())
    ]


def build_scroll_curve(db: Session, website_id: str, page_url: str) -> dict:
    events = (
        db.query(BehaviorEvent)
        .filter(
            BehaviorEvent.website_id == website_id,
            BehaviorEvent.page_url == page_url,
            BehaviorEvent.event_type == "scroll",
        )
        .all()
    )
    if not events:
        return {"avg_scroll_depth_pct": 0, "sessions": 0}

    max_depth_per_session: dict[str, float] = {}
    for event in events:
        depth = event.scroll_depth_pct or 0
        current = max_depth_per_session.get(event.session_id, 0)
        if depth > current:
            max_depth_per_session[event.session_id] = depth

    depths = list(max_depth_per_session.values())
    return {
        "avg_scroll_depth_pct": round(sum(depths) / len(depths), 1),
        "sessions": len(depths),
    }


def build_section_engagement(db: Session, website_id: str, page_url: str) -> list[dict]:
    """The key SEO-specific view: for each content section marked with
    data-slai-section="..." on the page, what % of sessions actually saw it."""
    pageviews = (
        db.query(BehaviorEvent.session_id)
        .filter(
            BehaviorEvent.website_id == website_id,
            BehaviorEvent.page_url == page_url,
            BehaviorEvent.event_type == "pageview",
        )
        .distinct()
        .count()
    )
    if pageviews == 0:
        return []

    section_views = (
        db.query(BehaviorEvent.section_id, BehaviorEvent.session_id)
        .filter(
            BehaviorEvent.website_id == website_id,
            BehaviorEvent.page_url == page_url,
            BehaviorEvent.event_type == "section_view",
            BehaviorEvent.section_id.isnot(None),
        )
        .distinct()
        .all()
    )

    counts: dict[str, int] = defaultdict(int)
    for section_id, _session_id in section_views:
        counts[section_id] += 1

    return [
        {
            "section_id": section_id,
            "views": views,
            "view_rate_pct": round(100 * views / pageviews, 1),
        }
        for section_id, views in sorted(counts.items(), key=lambda kv: -kv[1])
    ]


def cta_click_rate(db: Session, website_id: str, page_url: str) -> float:
    pageviews = (
        db.query(BehaviorEvent.session_id)
        .filter(
            BehaviorEvent.website_id == website_id,
            BehaviorEvent.page_url == page_url,
            BehaviorEvent.event_type == "pageview",
        )
        .distinct()
        .count()
    )
    if pageviews == 0:
        return 0.0

    cta_sessions = (
        db.query(BehaviorEvent.session_id)
        .filter(
            BehaviorEvent.website_id == website_id,
            BehaviorEvent.page_url == page_url,
            BehaviorEvent.event_type == "cta",
        )
        .distinct()
        .count()
    )
    return round(100 * cta_sessions / pageviews, 1)
