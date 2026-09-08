# Privacy and Data Collection

SearchLens AI's behaviour tracking (`sdk/tracker.js`) is built around
collecting the minimum data needed for SEO and UX analysis, not general
purpose user tracking. This document is a complete data map, useful both
for your own GDPR/privacy assessment and as a reference if this project
comes up in an interview.

## What is collected

| Event type | Fields | Notes |
|---|---|---|
| `pageview` | page URL, session ID, device type | Session ID is a random string, not tied to any personal identifier |
| `click` | x/y position as a **percentage of page dimensions** | Not pixel-exact, not tied to any DOM content or text |
| `scroll` | maximum scroll depth reached, as a percentage | |
| `section_view` | which `data-slai-section` element became visible | Only for elements the site owner explicitly marks |
| `cta` | which `data-slai-cta` element was clicked | Only for elements the site owner explicitly marks |
| `outbound` | destination hostname of an external link click | Not the full URL with query parameters |

## What is never collected

- Form field values, of any kind
- Passwords or authentication tokens
- Payment or billing information
- Full mouse movement traces or keystroke logs
- IP addresses are not stored by the application layer (your hosting
  provider's access logs are a separate concern, configure those
  independently)
- No cross-site tracking: `session_id` is stored in `sessionStorage`, scoped
  to a single browser tab's session on a single domain, not a persistent
  cross-site identifier

## Session identifiers

`sessionStorage` is used rather than a persistent cookie or `localStorage`,
so the session ID does not survive closing the tab and cannot be used to
build a long-term profile of a returning visitor. If sessionStorage is
unavailable (private browsing in some browsers), the SDK falls back to an
in-memory ID for that pageview only.

## Consent

The SDK supports a `requireConsent` flag (see `sdk/README.md`). When set,
no events are queued and no network request is made until the host page
calls `window.SearchLensAI.grantConsent()`, which should happen after your
own cookie/consent banner is accepted. This makes it straightforward to
wire into an existing consent management platform.

## Data retention

The reference implementation does not currently auto-delete old
`BehaviorEvent` rows. If you're running this for a real site under GDPR,
add a retention job (e.g. a scheduled task that deletes events older than
N months) before going to production. This is called out explicitly here
because it's the kind of gap that's easy to miss in a portfolio project but
matters in production.

## Server-side data

- `Website.api_key` should be treated as a secret for anything beyond the
  public tracking use case (it also grants read access to that site's data
  via `X-API-Key`, see `app/security.py`).
- Google service account JSON keys and AI provider API keys are read from
  environment variables (`.env`), never committed, and never returned by
  any API endpoint.
