"""
GEO / AEO visibility engine.

For each tracked query, we ask one or more AI providers the question the
way a real user would ("best fashion websites in Germany") and check
whether the brand and its competitors are mentioned, in what order, which
domains get cited as sources, and roughly what sentiment the mention has.

Providers are pluggable. Any provider without an API key configured is
skipped. If no provider is configured at all, a single "demo" provider
runs instead, using a seeded random generator so results are stable and
plausible without needing any API key. This mirrors how the rest of the
project handles missing credentials: it should always be possible to run
and demo the whole product with zero external accounts.
"""
from __future__ import annotations

import hashlib
import random
import re

import httpx

from app.config import get_settings

settings = get_settings()

CITATION_DOMAIN_POOL = [
    "wikipedia.org", "reddit.com", "trustpilot.com", "forbes.com",
    "techcrunch.com", "g2.com", "capterra.com", "producthunt.com",
    "medium.com", "quora.com",
]


def available_providers() -> list[str]:
    providers = []
    if settings.OPENAI_API_KEY:
        providers.append("openai")
    if settings.ANTHROPIC_API_KEY:
        providers.append("anthropic")
    if settings.PERPLEXITY_API_KEY:
        providers.append("perplexity")
    return providers or ["demo"]


def run_query(provider: str, query: str, brand: str, competitors: list[str]) -> dict:
    if provider == "openai":
        text = _ask_openai(query)
    elif provider == "anthropic":
        text = _ask_anthropic(query)
    elif provider == "perplexity":
        text = _ask_perplexity(query)
    else:
        text = _ask_demo(query, brand, competitors)

    return _analyse_response(text, brand, competitors)


# ---------- Provider calls ----------

def _ask_openai(query: str) -> str:
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": query}],
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _ask_anthropic(query: str) -> str:
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": query}],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return "".join(block.get("text", "") for block in data.get("content", []))


def _ask_perplexity(query: str) -> str:
    response = httpx.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": query}],
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _ask_demo(query: str, brand: str, competitors: list[str]) -> str:
    """Builds a plausible AI-answer-engine style response so the GEO
    dashboard is fully explorable with no API keys configured."""
    rnd = random.Random(hashlib.sha256(f"{query}::{brand}".encode()).hexdigest())
    all_brands = [brand] + competitors
    rnd.shuffle(all_brands)
    mentioned = [b for b in all_brands if rnd.random() < 0.75]
    if brand not in mentioned and rnd.random() < 0.5:
        mentioned.insert(rnd.randint(0, len(mentioned)), brand)

    domains = rnd.sample(CITATION_DOMAIN_POOL, k=min(3, len(CITATION_DOMAIN_POOL)))
    lines = [f"Here are some strong options for '{query}':"]
    for i, name in enumerate(mentioned, start=1):
        lines.append(f"{i}. {name}, a well known option in this space.")
    lines.append(f"Sources: {', '.join(domains)}.")
    return "\n".join(lines)


# ---------- Response analysis ----------

def _analyse_response(text: str, brand: str, competitors: list[str]) -> dict:
    lower = text.lower()
    brand_mentioned = brand.lower() in lower
    mention_position = None
    if brand_mentioned:
        # crude but effective: order of first appearance among all tracked names
        positions = {}
        for name in [brand] + competitors:
            idx = lower.find(name.lower())
            if idx != -1:
                positions[name] = idx
        ordered = sorted(positions, key=positions.get)
        if brand in ordered:
            mention_position = ordered.index(brand) + 1

    competitors_mentioned = [c for c in competitors if c.lower() in lower]

    cited_domains = sorted(set(re.findall(r"([a-z0-9-]+\.[a-z]{2,})", lower)))
    cited_domains = [d for d in cited_domains if not d.endswith((".png", ".jpg", ".svg"))][:10]

    sentiment = "neutral"
    positive_words = ["best", "great", "strong", "recommend", "trusted", "popular", "excellent"]
    negative_words = ["poor", "bad", "avoid", "complaint", "issue", "problem"]
    if any(w in lower for w in positive_words):
        sentiment = "positive"
    elif any(w in lower for w in negative_words):
        sentiment = "negative"

    return {
        "brand_mentioned": brand_mentioned,
        "mention_position": mention_position,
        "competitors_mentioned": competitors_mentioned,
        "cited_domains": cited_domains,
        "sentiment": sentiment,
        "raw_response": text,
    }


def summarise_runs(runs: list[dict]) -> dict:
    """Turns a list of GeoRun rows (as dicts) into the dashboard summary:
    an overall visibility score plus a per-provider breakdown."""
    if not runs:
        return {
            "visibility_score": 0, "brand_mention_rate": 0.0,
            "competitor_mention_rate": 0.0, "citation_rate": 0.0,
            "avg_mention_position": None, "by_provider": {}, "top_cited_domains": [],
        }

    total = len(runs)
    brand_mentions = sum(1 for r in runs if r["brand_mentioned"])
    competitor_mentions = sum(1 for r in runs if r["competitors_mentioned"])
    citations = sum(1 for r in runs if r["cited_domains"])
    positions = [r["mention_position"] for r in runs if r["mention_position"]]

    domain_counts: dict[str, int] = {}
    for r in runs:
        for d in r["cited_domains"]:
            domain_counts[d] = domain_counts.get(d, 0) + 1
    top_domains = sorted(domain_counts, key=domain_counts.get, reverse=True)[:8]

    by_provider: dict[str, dict] = {}
    for r in runs:
        p = by_provider.setdefault(r["provider"], {"total": 0, "mentioned": 0})
        p["total"] += 1
        if r["brand_mentioned"]:
            p["mentioned"] += 1
    for p in by_provider.values():
        p["mention_rate_pct"] = round(100 * p["mentioned"] / p["total"], 1)

    brand_rate = round(100 * brand_mentions / total, 1)
    competitor_rate = round(100 * competitor_mentions / total, 1)
    citation_rate = round(100 * citations / total, 1)
    avg_position = round(sum(positions) / len(positions), 1) if positions else None

    # Simple composite score: mention rate matters most, position and
    # citation presence adjust it up or down.
    position_bonus = 0
    if avg_position:
        position_bonus = max(0, 10 - avg_position)
    score = round(min(100, brand_rate * 0.7 + citation_rate * 0.2 + position_bonus))

    return {
        "visibility_score": score,
        "brand_mention_rate": brand_rate,
        "competitor_mention_rate": competitor_rate,
        "citation_rate": citation_rate,
        "avg_mention_position": avg_position,
        "by_provider": by_provider,
        "top_cited_domains": top_domains,
    }
