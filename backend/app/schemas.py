from datetime import datetime
from pydantic import BaseModel, Field


# ---------- Websites ----------

class WebsiteCreate(BaseModel):
    domain: str
    name: str
    gsc_property: str | None = None


class WebsiteOut(BaseModel):
    id: str
    domain: str
    name: str
    api_key: str
    gsc_property: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Crawl ----------

class CrawlRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, max_length=200)


class CrawlIssue(BaseModel):
    code: str
    severity: str  # "critical" | "warning" | "info"
    message: str


class CrawlResultOut(BaseModel):
    id: str
    url: str
    status_code: int | None
    response_time_ms: int | None
    title: str | None
    title_length: int | None
    meta_description: str | None
    meta_description_length: int | None
    h1_count: int | None
    canonical_url: str | None
    robots_meta: str | None
    word_count: int | None
    internal_links: int | None
    external_links: int | None
    images_missing_alt: int | None
    has_structured_data: bool
    structured_data_types: list[str]
    issues: list[dict]
    seo_score: int | None
    crawled_at: datetime

    class Config:
        from_attributes = True


# ---------- Tracking ----------

class TrackEvent(BaseModel):
    session_id: str
    page_url: str
    event_type: str
    x_pct: float | None = None
    y_pct: float | None = None
    scroll_depth_pct: float | None = None
    section_id: str | None = None
    duration_ms: int | None = None
    device_type: str | None = None
    meta: dict = {}


class TrackBatch(BaseModel):
    site_key: str
    events: list[TrackEvent]


class HeatmapCell(BaseModel):
    x_bucket: int
    y_bucket: int
    count: int


class SectionEngagement(BaseModel):
    section_id: str
    views: int
    view_rate_pct: float


# ---------- Search analytics ----------

class SearchSnapshotOut(BaseModel):
    source: str
    page_url: str
    query: str | None
    impressions: int
    clicks: int
    ctr: float
    avg_position: float | None

    class Config:
        from_attributes = True


# ---------- GEO ----------

class GeoConfigCreate(BaseModel):
    brand_name: str
    competitors: list[str] = []
    queries: list[str]


class GeoConfigOut(BaseModel):
    id: str
    brand_name: str
    competitors: list[str]
    queries: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class GeoRunOut(BaseModel):
    provider: str
    query: str
    brand_mentioned: bool
    mention_position: int | None
    competitors_mentioned: list[str]
    cited_domains: list[str]
    sentiment: str | None
    run_at: datetime

    class Config:
        from_attributes = True


class GeoSummary(BaseModel):
    visibility_score: int
    brand_mention_rate: float
    competitor_mention_rate: float
    citation_rate: float
    avg_mention_position: float | None
    by_provider: dict[str, dict]
    top_cited_domains: list[str]


# ---------- Insights ----------

class Insight(BaseModel):
    category: str  # technical | behaviour | search | geo
    severity: str  # info | opportunity | critical
    message: str
