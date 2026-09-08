"""
Populates the database with one demo website, a handful of behaviour
events and a GEO config, so a fresh clone has something to look at in the
dashboard immediately. Real crawl and GSC/GA4 data still uses the real
crawler and the demo-mode fallback in google_integrations.py; this script
only fabricates the behaviour events, since those need a live tracker.js
install to generate for real.

Run with:  python -m scripts.seed_demo_data
"""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, SessionLocal
from app.models import Website, BehaviorEvent, GeoConfig

DEMO_PAGE = "https://example.com/technical-seo-guide"


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    website = db.query(Website).filter(Website.domain == "example.com").first()
    if not website:
        website = Website(domain="example.com", name="Demo Site", gsc_property="sc-domain:example.com")
        db.add(website)
        db.commit()
        db.refresh(website)
        print(f"Created demo website. API key: {website.api_key}")
    else:
        print(f"Demo website already exists. API key: {website.api_key}")

    existing_events = db.query(BehaviorEvent).filter(BehaviorEvent.website_id == website.id).count()
    if existing_events == 0:
        sections = ["h1-intro", "pricing", "faq", "cta-primary", "technical-audit-section"]
        rnd = random.Random(42)
        events = []
        for i in range(400):
            session_id = f"demo-session-{i}"
            events.append(BehaviorEvent(
                website_id=website.id, session_id=session_id,
                page_url=DEMO_PAGE, event_type="pageview",
                device_type=rnd.choice(["desktop", "mobile", "tablet"]),
            ))
            for section in sections:
                view_chance = {"h1-intro": 0.95, "pricing": 0.7, "faq": 0.4,
                                "cta-primary": 0.18, "technical-audit-section": 0.35}[section]
                if rnd.random() < view_chance:
                    events.append(BehaviorEvent(
                        website_id=website.id, session_id=session_id,
                        page_url=DEMO_PAGE, event_type="section_view", section_id=section,
                    ))
            if rnd.random() < 0.18:
                events.append(BehaviorEvent(
                    website_id=website.id, session_id=session_id,
                    page_url=DEMO_PAGE, event_type="cta",
                ))
            for _ in range(rnd.randint(2, 8)):
                events.append(BehaviorEvent(
                    website_id=website.id, session_id=session_id,
                    page_url=DEMO_PAGE, event_type="click",
                    x_pct=rnd.uniform(0, 100), y_pct=rnd.uniform(0, 100),
                ))
            events.append(BehaviorEvent(
                website_id=website.id, session_id=session_id,
                page_url=DEMO_PAGE, event_type="scroll",
                scroll_depth_pct=rnd.uniform(20, 100),
            ))
        db.bulk_save_objects(events)
        db.commit()
        print(f"Seeded {len(events)} behaviour events for {DEMO_PAGE}")
    else:
        print("Behaviour events already seeded, skipping")

    if not db.query(GeoConfig).filter(GeoConfig.website_id == website.id).first():
        config = GeoConfig(
            website_id=website.id,
            brand_name="Example Co",
            competitors=["Rival Inc", "Acme Solutions"],
            queries=[
                "best example.com alternatives",
                "top tools like example.com",
                "is example.com worth it",
            ],
        )
        db.add(config)
        db.commit()
        print("Seeded a GEO config. POST /geo/run to generate demo AI visibility results.")

    db.close()


if __name__ == "__main__":
    run()
