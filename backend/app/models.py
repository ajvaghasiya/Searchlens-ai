import uuid
import secrets
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def gen_api_key() -> str:
    return "slai_" + secrets.token_urlsafe(24)


class Website(Base):
    """A site the user has registered with SearchLens AI."""
    __tablename__ = "websites"

    id = Column(String, primary_key=True, default=gen_uuid)
    domain = Column(String, nullable=False)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False, default=gen_api_key)
    gsc_property = Column(String, nullable=True)  # e.g. sc-domain:example.com
    created_at = Column(DateTime, default=datetime.utcnow)

    crawls = relationship("CrawlResult", back_populates="website", cascade="all, delete-orphan")
    events = relationship("BehaviorEvent", back_populates="website", cascade="all, delete-orphan")
    geo_configs = relationship("GeoConfig", back_populates="website", cascade="all, delete-orphan")


class CrawlResult(Base):
    """One crawled URL, with the raw technical SEO checks and a score."""
    __tablename__ = "crawl_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    website_id = Column(String, ForeignKey("websites.id"), nullable=False)
    url = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    title = Column(Text, nullable=True)
    title_length = Column(Integer, nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_description_length = Column(Integer, nullable=True)
    h1_count = Column(Integer, nullable=True)
    h1_text = Column(Text, nullable=True)
    canonical_url = Column(String, nullable=True)
    robots_meta = Column(String, nullable=True)
    word_count = Column(Integer, nullable=True)
    internal_links = Column(Integer, nullable=True)
    external_links = Column(Integer, nullable=True)
    images_missing_alt = Column(Integer, nullable=True)
    has_structured_data = Column(Boolean, default=False)
    structured_data_types = Column(JSON, default=list)
    issues = Column(JSON, default=list)   # list of {code, severity, message}
    seo_score = Column(Integer, nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="crawls")


class BehaviorEvent(Base):
    """A single raw interaction event sent by the tracker.js SDK."""
    __tablename__ = "behavior_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    website_id = Column(String, ForeignKey("websites.id"), nullable=False)
    session_id = Column(String, nullable=False)
    page_url = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # pageview, click, scroll, section_view, cta, outbound, session_end
    x_pct = Column(Float, nullable=True)          # click x position, 0-100 relative to page width
    y_pct = Column(Float, nullable=True)          # click y position, 0-100 relative to page height
    scroll_depth_pct = Column(Float, nullable=True)
    section_id = Column(String, nullable=True)    # data-slai-section value
    duration_ms = Column(Integer, nullable=True)
    device_type = Column(String, nullable=True)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="events")


class SearchSnapshot(Base):
    """Daily-ish snapshot pulled from Search Console / GA4 for one URL."""
    __tablename__ = "search_snapshots"

    id = Column(String, primary_key=True, default=gen_uuid)
    website_id = Column(String, ForeignKey("websites.id"), nullable=False)
    source = Column(String, nullable=False)  # "gsc" or "ga4"
    page_url = Column(String, nullable=False)
    query = Column(String, nullable=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    avg_position = Column(Float, nullable=True)
    sessions = Column(Integer, nullable=True)
    conversions = Column(Integer, nullable=True)
    date_range_start = Column(DateTime, nullable=True)
    date_range_end = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class GeoConfig(Base):
    """Brand / competitor / query set tracked for AI search visibility."""
    __tablename__ = "geo_configs"

    id = Column(String, primary_key=True, default=gen_uuid)
    website_id = Column(String, ForeignKey("websites.id"), nullable=False)
    brand_name = Column(String, nullable=False)
    competitors = Column(JSON, default=list)   # list[str]
    queries = Column(JSON, default=list)       # list[str]
    created_at = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="geo_configs")
    runs = relationship("GeoRun", back_populates="config", cascade="all, delete-orphan")


class GeoRun(Base):
    """One execution of the GEO/AEO visibility check across providers."""
    __tablename__ = "geo_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    config_id = Column(String, ForeignKey("geo_configs.id"), nullable=False)
    provider = Column(String, nullable=False)  # openai, anthropic, perplexity, demo
    query = Column(String, nullable=False)
    brand_mentioned = Column(Boolean, default=False)
    mention_position = Column(Integer, nullable=True)  # 1-based order of mention, if any
    competitors_mentioned = Column(JSON, default=list)
    cited_domains = Column(JSON, default=list)
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    raw_response = Column(Text, nullable=True)
    run_at = Column(DateTime, default=datetime.utcnow)

    config = relationship("GeoConfig", back_populates="runs")
