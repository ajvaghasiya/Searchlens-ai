# GEO / AEO Methodology

This document explains exactly how the AI visibility numbers in the GEO
module are calculated, so the score is never a black box.

## What gets tracked

For a given website you configure three things (`POST /geo/config`):

- **Brand name**, exactly as you'd expect an AI assistant to say it
- **Competitors**, the same way
- **Queries**, phrased the way a real user would type them into ChatGPT or
  Perplexity ("best project management tools for small teams"), not the
  way you'd type them into Google ("project management tools small teams")

## What happens on a run

`POST /geo/run` sends every query to every configured provider
(`app/services/geo.py`). For each response:

1. **Brand mentioned?** Case-insensitive substring match of the brand name
   in the response text.
2. **Mention position.** Among the brand and all tracked competitors, the
   order in which each name first appears in the text. Position 1 means
   the brand was named before any tracked competitor.
3. **Competitors mentioned.** Same substring check, per competitor.
4. **Cited domains.** A regex pass over the response text for
   `word.tld`-shaped strings, filtered to plausible domains. This is a
   heuristic, not a guarantee, since not every provider returns explicit
   source URLs in the message body. Providers with a real citations API
   (e.g. Perplexity's `citations` field) should be wired to use that field
   directly instead, this is noted as a roadmap item.
5. **Sentiment.** A simple keyword match against a small positive/negative
   word list. This is intentionally basic, a proper sentiment classifier is
   a reasonable upgrade if you need more precision.

## How the Visibility Score is calculated

```
visibility_score = min(100, brand_mention_rate * 0.7
                            + citation_rate * 0.2
                            + position_bonus)

position_bonus = max(0, 10 - avg_mention_position)   # rewards earlier mentions
```

Where `brand_mention_rate` and `citation_rate` are percentages across all
stored runs for the current config. The weighting (mention rate matters
most, citations and position adjust it) is a starting point, not a
claimed industry standard, tune `summarise_runs()` in `app/services/geo.py`
if you want different weighting.

## Demo mode

If no `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` or `PERPLEXITY_API_KEY` is set,
`available_providers()` returns `["demo"]`, and `_ask_demo()` generates a
plausible AI-answer-style response using a random generator seeded from the
query and brand name. This makes results stable across runs (the same query
always produces the same demo answer) without needing any external account.
Demo-mode results are clearly labelled with `provider: "demo"` in the
`GeoRun` rows, so they're never confused with real provider data when
looking at stored results.

## Known limitations

- No rate limiting or retry/backoff on provider calls yet.
- Domain extraction from response text is a heuristic; providers that
  return structured citations should be upgraded to use them directly.
- Sentiment analysis is a basic keyword match, not a trained classifier.
- Each `geo/run` call re-queries every configured query/provider pair, there
  is no caching or scheduling yet (see docs/architecture.md Roadmap).
