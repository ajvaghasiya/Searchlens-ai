from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GeoConfig, GeoRun
from app.schemas import GeoConfigCreate, GeoConfigOut, GeoRunOut, GeoSummary
from app.security import get_website_or_404
from app.services import geo as geo_service
from app.services.insights import build_geo_insight

router = APIRouter(prefix="/websites/{website_id}/geo", tags=["geo"])


@router.post("/config", response_model=GeoConfigOut)
def create_config(website_id: str, payload: GeoConfigCreate, db: Session = Depends(get_db)):
    get_website_or_404(website_id, db)
    config = GeoConfig(
        website_id=website_id,
        brand_name=payload.brand_name,
        competitors=payload.competitors,
        queries=payload.queries,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/config", response_model=GeoConfigOut | None)
def get_config(website_id: str, db: Session = Depends(get_db)):
    get_website_or_404(website_id, db)
    return (
        db.query(GeoConfig)
        .filter(GeoConfig.website_id == website_id)
        .order_by(GeoConfig.created_at.desc())
        .first()
    )


@router.post("/run", response_model=list[GeoRunOut])
def run_geo_check(website_id: str, db: Session = Depends(get_db)):
    """Runs every tracked query against every configured AI provider (or the
    demo provider if none are configured) and stores the results."""
    get_website_or_404(website_id, db)
    config = (
        db.query(GeoConfig)
        .filter(GeoConfig.website_id == website_id)
        .order_by(GeoConfig.created_at.desc())
        .first()
    )
    if not config:
        return []

    providers = geo_service.available_providers()
    saved: list[GeoRun] = []
    for query in config.queries:
        for provider in providers:
            result = geo_service.run_query(provider, query, config.brand_name, config.competitors)
            row = GeoRun(
                config_id=config.id,
                provider=provider,
                query=query,
                brand_mentioned=result["brand_mentioned"],
                mention_position=result["mention_position"],
                competitors_mentioned=result["competitors_mentioned"],
                cited_domains=result["cited_domains"],
                sentiment=result["sentiment"],
                raw_response=result["raw_response"],
            )
            db.add(row)
            saved.append(row)

    db.commit()
    for row in saved:
        db.refresh(row)
    return saved


@router.get("/summary")
def geo_summary(website_id: str, db: Session = Depends(get_db)):
    get_website_or_404(website_id, db)
    config = (
        db.query(GeoConfig)
        .filter(GeoConfig.website_id == website_id)
        .order_by(GeoConfig.created_at.desc())
        .first()
    )
    if not config:
        return {"summary": None, "insight": None, "runs": []}

    runs = db.query(GeoRun).filter(GeoRun.config_id == config.id).all()
    run_dicts = [
        {
            "provider": r.provider,
            "brand_mentioned": r.brand_mentioned,
            "mention_position": r.mention_position,
            "competitors_mentioned": r.competitors_mentioned,
            "cited_domains": r.cited_domains,
        }
        for r in runs
    ]
    summary = geo_service.summarise_runs(run_dicts)
    insight = build_geo_insight(summary, config.brand_name)
    return {"summary": summary, "insight": insight, "runs": [GeoRunOut.model_validate(r) for r in runs]}
