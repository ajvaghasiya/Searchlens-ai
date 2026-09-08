from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Website
from app.schemas import WebsiteCreate, WebsiteOut

router = APIRouter(prefix="/websites", tags=["websites"])


@router.post("", response_model=WebsiteOut)
def create_website(payload: WebsiteCreate, db: Session = Depends(get_db)):
    website = Website(
        domain=payload.domain,
        name=payload.name,
        gsc_property=payload.gsc_property,
    )
    db.add(website)
    db.commit()
    db.refresh(website)
    return website


@router.get("", response_model=list[WebsiteOut])
def list_websites(db: Session = Depends(get_db)):
    return db.query(Website).order_by(Website.created_at.desc()).all()


@router.get("/{website_id}", response_model=WebsiteOut)
def get_website(website_id: str, db: Session = Depends(get_db)):
    from app.security import get_website_or_404
    return get_website_or_404(website_id, db)
