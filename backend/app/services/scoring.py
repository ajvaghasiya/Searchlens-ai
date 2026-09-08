"""
Turns the raw issue list from the crawler into a single 0-100 "SEO Health
Score" per page. Weights are deliberately simple and documented here rather
than hidden in a black box, since the whole point of this module is to be
able to explain a score in an interview or a client meeting.
"""
from app.services.crawler import PageCheckResult

SEVERITY_PENALTY = {
    "critical": 20,
    "warning": 8,
    "info": 2,
}

MAX_SCORE = 100


def score_page(page: PageCheckResult) -> int:
    if page.error or (page.status_code and page.status_code >= 400):
        return 0

    score = MAX_SCORE
    for issue in page.issues:
        score -= SEVERITY_PENALTY.get(issue["severity"], 0)

    return max(0, min(MAX_SCORE, score))


def score_site(pages: list[PageCheckResult]) -> dict:
    """Aggregate score plus a breakdown, used for the site-level dashboard."""
    if not pages:
        return {"score": 0, "pages_crawled": 0, "critical_issues": 0, "warning_issues": 0}

    scores = [score_page(p) for p in pages]
    critical = sum(1 for p in pages for i in p.issues if i["severity"] == "critical")
    warnings = sum(1 for p in pages for i in p.issues if i["severity"] == "warning")

    return {
        "score": round(sum(scores) / len(scores)),
        "pages_crawled": len(pages),
        "critical_issues": critical,
        "warning_issues": warnings,
    }
