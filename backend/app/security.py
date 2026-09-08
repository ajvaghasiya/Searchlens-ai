"""
MVP auth: each registered site gets a random API key (see models.Website).
The dashboard stores that key client-side and sends it as a header for any
site-scoped request. The public tracking endpoint uses a separate, safe to
expose "site key" (same value, different name) since it has to sit in
public JavaScript on the customer's website.

This is intentionally simple. Multi-user accounts with proper JWT auth and
per-user roles are on the roadmap, see docs/architecture.md.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Website


def get_website_by_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Website:
    website = db.query(Website).filter(Website.api_key == x_api_key).first()
    if not website:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return website


def get_website_or_404(website_id: str, db: Session) -> Website:
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    return website
