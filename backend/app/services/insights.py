"""
This is what turns four separate data sources into the "AI recommendation"
line the dashboard shows for each page. It is rule-based rather than a
model call, on purpose: the rules encode real SEO heuristics (expected CTR
curves, engagement thresholds, thin content limits) and are easy to explain
and extend. An LLM-written narrative version of the same rules is a natural
next step and is noted in docs/architecture.md as a roadmap item.
"""
from app.services.google_integrations import EXPECTED_CTR_BY_POSITION


def build_page_insights(
    crawl: dict | None,
    section_engagement: list[dict],
    cta_rate: float | None,
    gsc_row: dict | None,
) -> list[dict]:
    insights: list[dict] = []

    if crawl:
        for issue in crawl.get("issues", []):
            if issue["severity"] == "critical":
                insights.append({
                    "category": "technical",
                    "severity": "critical",
                    "message": issue["message"],
                })

    if gsc_row and gsc_row.get("avg_position"):
        position = gsc_row["avg_position"]
        bucket = max(1, min(10, round(position)))
        expected = EXPECTED_CTR_BY_POSITION.get(bucket)
        actual = gsc_row.get("ctr", 0)
        if expected and actual < expected * 0.7 and gsc_row.get("impressions", 0) > 500:
            insights.append({
                "category": "search",
                "severity": "opportunity",
                "message": (
                    f"The page ranks around position {position:.1f} and gets meaningful impressions, "
                    f"but CTR ({actual * 100:.2f}%) is well below the {expected * 100:.1f}% expected at "
                    "that position. Consider testing the title tag and meta description."
                ),
            })

    if section_engagement:
        weakest = min(section_engagement, key=lambda s: s["view_rate_pct"])
        strongest = max(section_engagement, key=lambda s: s["view_rate_pct"])
        if weakest["view_rate_pct"] < 40:
            insights.append({
                "category": "behaviour",
                "severity": "opportunity",
                "message": (
                    f"Only {weakest['view_rate_pct']}% of visitors reach the "
                    f"'{weakest['section_id']}' section. If it targets an important keyword, "
                    "moving it higher on the page is likely to help."
                ),
            })
        if strongest["view_rate_pct"] > 80 and strongest["section_id"] != weakest["section_id"]:
            insights.append({
                "category": "behaviour",
                "severity": "info",
                "message": (
                    f"The '{strongest['section_id']}' section is seen by "
                    f"{strongest['view_rate_pct']}% of visitors. Strong candidate for "
                    "expanding with more keyword-relevant content."
                ),
            })

    if cta_rate is not None and cta_rate < 15:
        insights.append({
            "category": "behaviour",
            "severity": "opportunity",
            "message": (
                f"Only {cta_rate}% of sessions interact with the primary call to action. "
                "Worth checking CTA placement against the scroll depth data."
            ),
        })

    if not insights:
        insights.append({
            "category": "technical",
            "severity": "info",
            "message": "No significant issues detected across technical, search or behaviour data.",
        })

    return insights


def build_geo_insight(summary: dict, brand: str) -> dict:
    rate = summary["brand_mention_rate"]
    competitor_rate = summary["competitor_mention_rate"]
    citation_rate = summary["citation_rate"]

    if rate < competitor_rate and citation_rate < 50:
        message = (
            f"{brand} is mentioned in {rate}% of tracked AI answers, below the "
            f"{competitor_rate}% rate for tracked competitors, and cited sources back it up "
            f"only {citation_rate}% of the time. Building consistent brand mentions across "
            "third-party sites (reviews, comparisons, community threads) is likely to help "
            "more than on-site changes alone."
        )
        severity = "opportunity"
    elif rate >= 70:
        message = (
            f"{brand} already appears in {rate}% of tracked AI answers. "
            "Focus on maintaining citation quality and monitoring new competitor entrants."
        )
        severity = "info"
    else:
        message = (
            f"{brand} is mentioned in {rate}% of tracked AI answers, roughly in line with "
            f"competitors ({competitor_rate}%). Expanding the tracked query set will give a "
            "clearer picture of where the gaps are."
        )
        severity = "info"

    return {"category": "geo", "severity": severity, "message": message}
