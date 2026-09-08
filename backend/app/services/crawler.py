"""
A small, dependency-light technical SEO crawler.

It fetches a single URL, parses it with BeautifulSoup and returns a plain
dict of checks. This intentionally covers the same ground as the free tier
of a tool like Screaming Frog: status codes, titles, meta descriptions,
headings, canonicals, robots directives, internal/external link counts,
missing alt text, structured data and basic word count.

The crawler is synchronous and single-page by design. crawl_site() below
does a bounded breadth-first crawl across a domain for the "audit a whole
site" use case, but stays intentionally simple: no JS rendering, no
sitemap parsing yet (see docs/architecture.md for the roadmap).
"""
from __future__ import annotations

import time
import json
from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "SearchLensAI-Crawler/0.1 (+https://github.com/searchlens-ai/searchlens)"
TIMEOUT_SECONDS = 10


@dataclass
class PageCheckResult:
    url: str
    status_code: int | None = None
    response_time_ms: int | None = None
    title: str | None = None
    meta_description: str | None = None
    h1_count: int = 0
    h1_text: str | None = None
    canonical_url: str | None = None
    robots_meta: str | None = None
    word_count: int = 0
    internal_links: int = 0
    external_links: int = 0
    images_missing_alt: int = 0
    has_structured_data: bool = False
    structured_data_types: list[str] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    error: str | None = None

    @property
    def title_length(self) -> int:
        return len(self.title) if self.title else 0

    @property
    def meta_description_length(self) -> int:
        return len(self.meta_description) if self.meta_description else 0


def _add_issue(result: PageCheckResult, code: str, severity: str, message: str) -> None:
    result.issues.append({"code": code, "severity": severity, "message": message})


def crawl_page(url: str, timeout: int = TIMEOUT_SECONDS) -> PageCheckResult:
    """Fetch and analyse a single URL. Never raises: network/parse errors are
    captured on the result so a bad URL doesn't take down a batch crawl."""
    result = PageCheckResult(url=url)
    headers = {"User-Agent": USER_AGENT}

    start = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        result.error = str(exc)
        _add_issue(result, "fetch_failed", "critical", f"Could not fetch URL: {exc}")
        return result
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    result.status_code = response.status_code
    result.response_time_ms = elapsed_ms

    if response.status_code >= 400:
        _add_issue(result, "bad_status", "critical", f"Page returned HTTP {response.status_code}")
        return result

    if elapsed_ms > 2000:
        _add_issue(result, "slow_response", "warning", f"Server took {elapsed_ms} ms to respond")

    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type:
        _add_issue(result, "non_html", "info", f"Content-Type is '{content_type}', skipping HTML checks")
        return result

    soup = BeautifulSoup(response.text, "lxml")

    _check_title(soup, result)
    _check_meta_description(soup, result)
    _check_headings(soup, result)
    _check_canonical(soup, result, url)
    _check_robots_meta(soup, result)
    _check_links(soup, result, url)
    _check_images(soup, result)
    _check_structured_data(soup, result)
    _check_content_length(soup, result)

    return result


def _check_title(soup: BeautifulSoup, result: PageCheckResult) -> None:
    tag = soup.find("title")
    if not tag or not tag.text.strip():
        _add_issue(result, "missing_title", "critical", "Page has no <title> tag")
        return
    result.title = tag.text.strip()
    length = len(result.title)
    if length < 15:
        _add_issue(result, "title_too_short", "warning", f"Title is only {length} characters")
    elif length > 60:
        _add_issue(result, "title_too_long", "warning", f"Title is {length} characters, may be truncated in search results")


def _check_meta_description(soup: BeautifulSoup, result: PageCheckResult) -> None:
    tag = soup.find("meta", attrs={"name": "description"})
    content = tag.get("content", "").strip() if tag else ""
    if not content:
        _add_issue(result, "missing_meta_description", "warning", "Page has no meta description")
        return
    result.meta_description = content
    length = len(content)
    if length < 70:
        _add_issue(result, "meta_description_short", "info", f"Meta description is only {length} characters")
    elif length > 160:
        _add_issue(result, "meta_description_long", "warning", f"Meta description is {length} characters, may be truncated")


def _check_headings(soup: BeautifulSoup, result: PageCheckResult) -> None:
    h1s = soup.find_all("h1")
    result.h1_count = len(h1s)
    result.h1_text = h1s[0].get_text(strip=True) if h1s else None
    if len(h1s) == 0:
        _add_issue(result, "missing_h1", "critical", "Page has no <h1>")
    elif len(h1s) > 1:
        _add_issue(result, "multiple_h1", "warning", f"Page has {len(h1s)} <h1> tags")


def _check_canonical(soup: BeautifulSoup, result: PageCheckResult, url: str) -> None:
    tag = soup.find("link", rel="canonical")
    if not tag or not tag.get("href"):
        _add_issue(result, "missing_canonical", "info", "Page has no canonical tag")
        return
    canonical = urljoin(url, tag["href"])
    result.canonical_url = canonical
    if urlparse(canonical).path.rstrip("/") != urlparse(url).path.rstrip("/"):
        _add_issue(result, "canonical_mismatch", "info", "Canonical URL points to a different page")


def _check_robots_meta(soup: BeautifulSoup, result: PageCheckResult) -> None:
    tag = soup.find("meta", attrs={"name": "robots"})
    content = tag.get("content", "").strip().lower() if tag else None
    result.robots_meta = content
    if content and ("noindex" in content):
        _add_issue(result, "noindex", "critical", "Page is set to noindex")


def _check_links(soup: BeautifulSoup, result: PageCheckResult, url: str) -> None:
    domain = urlparse(url).netloc
    internal, external = 0, 0
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        absolute = urljoin(url, href)
        if urlparse(absolute).netloc == domain:
            internal += 1
        else:
            external += 1
    result.internal_links = internal
    result.external_links = external
    if internal == 0:
        _add_issue(result, "no_internal_links", "warning", "Page has no internal links")


def _check_images(soup: BeautifulSoup, result: PageCheckResult) -> None:
    images = soup.find_all("img")
    missing = sum(1 for img in images if not img.get("alt", "").strip())
    result.images_missing_alt = missing
    if missing:
        _add_issue(result, "images_missing_alt", "warning", f"{missing} image(s) missing alt text")


def _check_structured_data(soup: BeautifulSoup, result: PageCheckResult) -> None:
    scripts = soup.find_all("script", type="application/ld+json")
    types: list[str] = []
    for script in scripts:
        try:
            data = json.loads(script.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and "@type" in item:
                types.append(item["@type"] if isinstance(item["@type"], str) else str(item["@type"]))
    result.has_structured_data = bool(types)
    result.structured_data_types = types
    if not types:
        _add_issue(result, "no_structured_data", "info", "No JSON-LD structured data found")


def _check_content_length(soup: BeautifulSoup, result: PageCheckResult) -> None:
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    words = text.split()
    result.word_count = len(words)
    if result.word_count < 200:
        _add_issue(result, "thin_content", "warning", f"Page has only {result.word_count} words")


def crawl_site(start_url: str, max_pages: int = 25) -> list[PageCheckResult]:
    """Bounded breadth-first crawl of internal links starting from start_url.
    Kept deliberately simple: same-domain only, no robots.txt parsing yet,
    no JS rendering. Good enough for a portfolio demo and small marketing
    sites; see docs/architecture.md for the Playwright-based roadmap."""
    domain = urlparse(start_url).netloc
    seen: set[str] = {start_url}
    queue: deque[str] = deque([start_url])
    results: list[PageCheckResult] = []

    while queue and len(results) < max_pages:
        url = queue.popleft()
        page = crawl_page(url)
        results.append(page)

        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS)
            soup = BeautifulSoup(response.text, "lxml")
        except requests.RequestException:
            continue

        for a in soup.find_all("a", href=True):
            absolute = urljoin(url, a["href"].split("#")[0])
            parsed = urlparse(absolute)
            if parsed.netloc == domain and absolute not in seen and len(seen) < max_pages * 4:
                seen.add(absolute)
                queue.append(absolute)

    return results
