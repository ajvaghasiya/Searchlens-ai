"""
Search Console and GA4 integration.

Real mode: uses a Google service account (simpler to set up and document
than a full 3-legged OAuth flow for a tool like this). Steps to enable are
in docs/architecture.md and the root README.

Demo mode: if no service account is configured, both functions return
deterministic synthetic data seeded from the page URL, so the dashboard is
always explorable without any Google account at all. Numbers are clearly
plausible SEO data (impressions, clicks, CTR, position) rather than random
noise, which is what makes the demo useful for screenshots and interviews.
"""
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta

from app.config import get_settings

settings = get_settings()


def _seeded_random(*parts: str) -> random.Random:
    seed = hashlib.sha256("::".join(parts).encode()).hexdigest()
    return random.Random(seed)


def _credentials_available() -> bool:
    return bool(settings.GOOGLE_SERVICE_ACCOUNT_JSON) and not settings.FORCE_DEMO_MODE


def get_search_console_data(gsc_property: str, pages: list[str]) -> list[dict]:
    if _credentials_available():
        return _fetch_real_gsc_data(gsc_property, pages)
    return [_demo_gsc_row(gsc_property, url) for url in pages]


def get_ga4_data(pages: list[str]) -> list[dict]:
    if _credentials_available() and settings.GA4_PROPERTY_ID:
        return _fetch_real_ga4_data(pages)
    return [_demo_ga4_row(url) for url in pages]


# ---------- Real implementations ----------

def _fetch_real_gsc_data(gsc_property: str, pages: list[str]) -> list[dict]:
    """Requires GOOGLE_SERVICE_ACCOUNT_JSON pointing at a service account key
    that has been added as a user on the Search Console property."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    service = build("searchconsole", "v1", credentials=creds)

    end = datetime.utcnow().date()
    start = end - timedelta(days=28)

    rows: list[dict] = []
    for url in pages:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query"],
            "dimensionFilterGroups": [{
                "filters": [{"dimension": "page", "operator": "equals", "expression": url}]
            }],
            "rowLimit": 10,
        }
        response = service.searchanalytics().query(siteUrl=gsc_property, body=body).execute()
        for row in response.get("rows", []):
            rows.append({
                "page_url": url,
                "query": row["keys"][0],
                "impressions": row.get("impressions", 0),
                "clicks": row.get("clicks", 0),
                "ctr": row.get("ctr", 0.0),
                "avg_position": row.get("position"),
            })
    return rows


def _fetch_real_ga4_data(pages: list[str]) -> list[dict]:
    """Requires GA4_PROPERTY_ID and a service account with Viewer access on
    the GA4 property, using the Google Analytics Data API."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    service = build("analyticsdata", "v1beta", credentials=creds)

    rows: list[dict] = []
    for url in pages:
        body = {
            "dateRanges": [{"startDate": "28daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "pagePath"}],
            "metrics": [{"name": "sessions"}, {"name": "conversions"}],
            "dimensionFilter": {
                "filter": {"fieldName": "pagePath", "stringFilter": {"value": url}}
            },
        }
        response = service.properties().runReport(
            property=f"properties/{settings.GA4_PROPERTY_ID}", body=body
        ).execute()
        for row in response.get("rows", []):
            metrics = row["metricValues"]
            rows.append({
                "page_url": url,
                "sessions": int(metrics[0]["value"]),
                "conversions": int(metrics[1]["value"]),
            })
    return rows


# ---------- Demo generators ----------

EXPECTED_CTR_BY_POSITION = {
    1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.06,
    6: 0.045, 7: 0.035, 8: 0.03, 9: 0.025, 10: 0.02,
}


def _demo_gsc_row(gsc_property: str, url: str) -> dict:
    rnd = _seeded_random(gsc_property, url, "gsc")
    position = round(rnd.uniform(3, 18), 1)
    impressions = rnd.randint(500, 80000)
    bucket = max(1, min(10, round(position)))
    expected_ctr = EXPECTED_CTR_BY_POSITION.get(bucket, 0.015)
    # Occasionally simulate an underperforming page (CTR well below expected)
    ctr_multiplier = rnd.choice([0.4, 0.6, 0.9, 1.0, 1.1, 1.3])
    ctr = round(expected_ctr * ctr_multiplier, 4)
    clicks = max(0, round(impressions * ctr))

    return {
        "page_url": url,
        "query": None,
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr,
        "avg_position": position,
        "expected_ctr": expected_ctr,
    }


def _demo_ga4_row(url: str) -> dict:
    rnd = _seeded_random(url, "ga4")
    sessions = rnd.randint(200, 20000)
    conversions = round(sessions * rnd.uniform(0.005, 0.06))
    return {"page_url": url, "sessions": sessions, "conversions": conversions}
