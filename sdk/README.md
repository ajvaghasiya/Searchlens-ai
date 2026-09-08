# tracker.js

A dependency-free, ~6KB JavaScript SDK that collects privacy-safe interaction
data and sends it to the SearchLens AI behaviour analytics module.

## Install

Add this before the closing `</body>` tag of any page you want to track:

```html
<script>
  window.SearchLensConfig = {
    siteKey: "slai_your_site_key_here",
    apiEndpoint: "https://your-api-domain.com/api/v1/track" // optional, defaults shown in tracker.js
  };
</script>
<script src="https://your-api-domain.com/tracker.js" defer></script>
```

Get `siteKey` by registering a site: `POST /api/v1/websites`, the response
includes an `api_key` field, that value is your site key.

## Mark up content sections

To get SEO-specific "who actually saw this" data, add a `data-slai-section`
attribute to any content block you care about:

```html
<section data-slai-section="pricing">...</section>
<section data-slai-section="faq">...</section>
```

Mark your primary call to action the same way:

```html
<a href="/signup" data-slai-cta="primary-cta">Start free trial</a>
```

## What it tracks

| Signal | How |
|---|---|
| Page views | one event per load |
| Clicks | x/y position as a % of page size, not pixel-exact user identifiers |
| Scroll depth | maximum scroll % reached per session |
| Section visibility | via `IntersectionObserver`, only for elements with `data-slai-section` |
| CTA interaction | via `data-slai-cta` |
| Outbound link clicks | any link to a different hostname |
| Device type | derived from viewport width, not a fingerprint |

## What it never tracks

Form field values, passwords, payment details, or anything that isn't
interaction metadata. See [`/docs/privacy.md`](../docs/privacy.md) for the
full data map and GDPR notes.

## Consent gating

If you need to wait for cookie/consent banner acceptance before any network
call is made:

```html
<script>
  window.SearchLensConfig = { siteKey: "slai_xxx", requireConsent: true };
</script>
<script src=".../tracker.js" defer></script>
<script>
  // once your consent banner is accepted:
  window.SearchLensAI.grantConsent();
</script>
```

With `requireConsent: true`, the SDK loads but stays fully inactive
(no events queued, no network calls) until `grantConsent()` is called.
