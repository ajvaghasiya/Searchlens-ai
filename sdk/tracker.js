/*!
 * SearchLens AI tracker.js
 * Lightweight, dependency-free behaviour tracking SDK.
 *
 * Usage:
 *   <script>
 *     window.SearchLensConfig = { siteKey: "slai_xxxxxxxx" };
 *   </script>
 *   <script src="https://your-api-domain.com/tracker.js" defer></script>
 *
 * Mark content sections you want SEO-relevant engagement data for:
 *   <section data-slai-section="pricing">...</section>
 *
 * Mark your primary call to action:
 *   <a href="/signup" data-slai-cta="primary-cta">Start free trial</a>
 *
 * Privacy: this SDK never reads form field values, passwords or payment
 * details. It only records interaction metadata (coordinates as a % of
 * page size, scroll depth, which marked sections became visible, and
 * outbound link clicks). See /docs/privacy.md for the full data map and
 * for how to wire this up to a consent banner.
 */
(function (window, document) {
  "use strict";

  var config = window.SearchLensConfig || {};
  if (!config.siteKey) {
    console.warn("[SearchLens AI] Missing window.SearchLensConfig.siteKey, tracker disabled.");
    return;
  }

  var API_ENDPOINT = config.apiEndpoint || "https://api.searchlens.ai/api/v1/track";
  var FLUSH_INTERVAL_MS = config.flushIntervalMs || 5000;
  var BATCH_LIMIT = 25;

  var sessionId = getOrCreateSessionId();
  var queue = [];
  var maxScrollDepth = 0;
  var seenSections = {};
  var consentGiven = !config.requireConsent; // if consent isn't required, tracking starts immediately

  function getOrCreateSessionId() {
    try {
      var existing = sessionStorage.getItem("slai_session_id");
      if (existing) return existing;
      var id = "s_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem("slai_session_id", id);
      return id;
    } catch (e) {
      // sessionStorage unavailable (privacy mode, etc). Fall back to an
      // in-memory id, which just means each pageview looks like a new session.
      return "s_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
    }
  }

  function deviceType() {
    var w = window.innerWidth;
    if (w < 640) return "mobile";
    if (w < 1024) return "tablet";
    return "desktop";
  }

  function pushEvent(event) {
    if (!consentGiven) return;
    event.session_id = sessionId;
    event.page_url = location.href.split("#")[0];
    event.device_type = deviceType();
    queue.push(event);
    if (queue.length >= BATCH_LIMIT) flush();
  }

  function flush(useBeacon) {
    if (!consentGiven || queue.length === 0) return;
    var payload = JSON.stringify({ site_key: config.siteKey, events: queue });
    queue = [];

    if (useBeacon && navigator.sendBeacon) {
      var blob = new Blob([payload], { type: "application/json" });
      navigator.sendBeacon(API_ENDPOINT, blob);
      return;
    }

    fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
      keepalive: true,
    }).catch(function () {
      /* silently drop on network failure, analytics should never break the page */
    });
  }

  function trackPageview() {
    pushEvent({ event_type: "pageview" });
  }

  function trackClicks() {
    document.addEventListener(
      "click",
      function (e) {
        var x_pct = (e.pageX / document.documentElement.scrollWidth) * 100;
        var y_pct = (e.pageY / document.documentElement.scrollHeight) * 100;
        pushEvent({ event_type: "click", x_pct: round2(x_pct), y_pct: round2(y_pct) });

        var ctaEl = e.target.closest("[data-slai-cta]");
        if (ctaEl) {
          pushEvent({ event_type: "cta", meta: { cta_id: ctaEl.getAttribute("data-slai-cta") } });
        }

        var link = e.target.closest("a[href]");
        if (link && isOutbound(link.href)) {
          pushEvent({ event_type: "outbound", meta: { href: link.href } });
        }
      },
      { capture: true }
    );
  }

  function isOutbound(href) {
    try {
      return new URL(href, location.href).hostname !== location.hostname;
    } catch (e) {
      return false;
    }
  }

  function trackScroll() {
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var scrollTop = window.scrollY;
        var docHeight = document.documentElement.scrollHeight - window.innerHeight;
        var depth = docHeight > 0 ? (scrollTop / docHeight) * 100 : 100;
        if (depth > maxScrollDepth) {
          maxScrollDepth = Math.min(100, depth);
          pushEvent({ event_type: "scroll", scroll_depth_pct: round2(maxScrollDepth) });
        }
        ticking = false;
      });
    });
  }

  function trackSectionVisibility() {
    var sections = document.querySelectorAll("[data-slai-section]");
    if (!sections.length || !("IntersectionObserver" in window)) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var id = entry.target.getAttribute("data-slai-section");
          if (entry.isIntersecting && !seenSections[id]) {
            seenSections[id] = true;
            pushEvent({ event_type: "section_view", section_id: id });
          }
        });
      },
      { threshold: 0.5 }
    );

    sections.forEach(function (el) {
      observer.observe(el);
    });
  }

  function round2(n) {
    return Math.round(n * 100) / 100;
  }

  function init() {
    trackPageview();
    trackClicks();
    trackScroll();
    trackSectionVisibility();

    setInterval(flush, FLUSH_INTERVAL_MS);
    window.addEventListener("beforeunload", function () {
      flush(true);
    });
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") flush(true);
    });
  }

  // Public API, mainly for consent-gated setups:
  //   SearchLensAI.grantConsent() once the user accepts the cookie/consent banner.
  window.SearchLensAI = {
    grantConsent: function () {
      consentGiven = true;
      init();
    },
    flush: function () {
      flush();
    },
  };

  if (consentGiven) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})(window, document);
