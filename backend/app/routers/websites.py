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


import httpx
from app.schemas import AutomationLogCreate, AutomationLogOut
from app.models import AutomationLog

@router.post("/{website_id}/trigger-automation")
def trigger_automation(website_id: str, db: Session = Depends(get_db)):
    from app.security import get_website_or_404
    website = get_website_or_404(website_id, db)
    # Fire and forget request to n8n webhook
    url = f"http://n8n:5678/webhook/run-monitoring?website_id={website.id}&domain={website.domain}"
    
    try:
        response = httpx.post(url, timeout=5.0)
        return {"status": "triggered", "n8n_response": response.text}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/{website_id}/automation-log", response_model=AutomationLogOut)
def create_automation_log(website_id: str, payload: AutomationLogCreate, db: Session = Depends(get_db)):
    from app.security import get_website_or_404
    website = get_website_or_404(website_id, db)
    log = AutomationLog(
        website_id=website.id,
        message=payload.message,
        status=payload.status
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/{website_id}/automation-log", response_model=list[AutomationLogOut])
def get_automation_logs(website_id: str, db: Session = Depends(get_db)):
    from app.security import get_website_or_404
    website = get_website_or_404(website_id, db)
    return db.query(AutomationLog).filter(AutomationLog.website_id == website.id).order_by(AutomationLog.timestamp.desc()).all()
