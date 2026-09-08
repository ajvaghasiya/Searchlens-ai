"use client";

import { useEffect, useState } from "react";
import {
  api,
  Website,
  CrawlResult,
  HeatmapData,
  SearchRow,
  GeoSummary,
  Insight,
} from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { ScoreGauge } from "@/components/ScoreGauge";
import { Heatmap } from "@/components/Heatmap";
import { BarChart } from "@/components/BarChart";

type Tab = "overview" | "technical" | "behaviour" | "search" | "geo";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "technical", label: "Technical SEO" },
  { id: "behaviour", label: "Behaviour" },
  { id: "search", label: "Search Analytics" },
  { id: "geo", label: "AI Visibility (GEO)" },
];

const severityColor: Record<string, string> = {
  critical: "text-red-600 bg-red-50 border-red-200",
  opportunity: "text-amber-700 bg-amber-50 border-amber-200",
  info: "text-slate-600 bg-slate-50 border-slate-200",
};

export default function DashboardPage() {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [websiteId, setWebsiteId] = useState<string>("");
  const [pageUrl, setPageUrl] = useState("https://example.com/technical-seo-guide");
  const [tab, setTab] = useState<Tab>("overview");
  const [loadingSites, setLoadingSites] = useState(true);

  useEffect(() => {
    api
      .listWebsites()
      .then((sites) => {
        setWebsites(sites);
        if (sites.length && !websiteId) setWebsiteId(sites[0].id);
      })
      .catch(() => {})
      .finally(() => setLoadingSites(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
        <NewSiteForm
          onCreated={(site) => {
            setWebsites((prev) => [site, ...prev]);
            setWebsiteId(site.id);
          }}
        />
      </div>

      <div className="card mb-6 flex flex-wrap items-end gap-4">
        <div className="flex-1 min-w-[220px]">
          <label className="text-xs text-slate-500">Website</label>
          <select
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
            value={websiteId}
            onChange={(e) => setWebsiteId(e.target.value)}
          >
            {loadingSites && <option>Loading...</option>}
            {!loadingSites && websites.length === 0 && <option>No websites yet, create one</option>}
            {websites.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} ({w.domain})
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1 min-w-[280px]">
          <label className="text-xs text-slate-500">Page URL</label>
          <input
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
            value={pageUrl}
            onChange={(e) => setPageUrl(e.target.value)}
          />
        </div>
      </div>

      <div className="flex gap-1 border-b border-slate-200 mb-6">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              tab === t.id
                ? "border-accent text-accent"
                : "border-transparent text-slate-500 hover:text-ink"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {!websiteId ? (
        <p className="text-sm text-slate-500">Create a website above to get started.</p>
      ) : (
        <>
          {tab === "overview" && <OverviewTab websiteId={websiteId} pageUrl={pageUrl} />}
          {tab === "technical" && <TechnicalTab websiteId={websiteId} pageUrl={pageUrl} />}
          {tab === "behaviour" && <BehaviourTab websiteId={websiteId} pageUrl={pageUrl} />}
          {tab === "search" && <SearchTab websiteId={websiteId} />}
          {tab === "geo" && <GeoTab websiteId={websiteId} />}
        </>
      )}
    </div>
  );
}

function NewSiteForm({ onCreated }: { onCreated: (site: Website) => void }) {
  const [open, setOpen] = useState(false);
  const [domain, setDomain] = useState("");
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  if (!open) {
    return (
      <button className="btn-secondary text-sm" onClick={() => setOpen(true)}>
        + Add website
      </button>
    );
  }

  return (
    <form
      className="flex items-end gap-2"
      onSubmit={async (e) => {
        e.preventDefault();
        if (!domain || !name) return;
        setSaving(true);
        try {
          const site = await api.createWebsite({ domain, name });
          onCreated(site);
          setOpen(false);
          setDomain("");
          setName("");
        } finally {
          setSaving(false);
        }
      }}
    >
      <input
        placeholder="example.com"
        className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        value={domain}
        onChange={(e) => setDomain(e.target.value)}
      />
      <input
        placeholder="Display name"
        className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <button className="btn-primary text-sm" disabled={saving}>
        {saving ? "Saving..." : "Create"}
      </button>
    </form>
  );
}

function InsightsList({ insights }: { insights: Insight[] }) {
  return (
    <div className="card">
      <p className="text-sm font-medium text-ink mb-3">Recommendations</p>
      <div className="space-y-2">
        {insights.map((insight, i) => (
          <div
            key={i}
            className={`text-sm border rounded-lg px-3 py-2 ${severityColor[insight.severity] || severityColor.info}`}
          >
            <span className="uppercase text-[10px] font-semibold tracking-wide mr-2">
              {insight.category}
            </span>
            {insight.message}
          </div>
        ))}
      </div>
    </div>
  );
}

function OverviewTab({ websiteId, pageUrl }: { websiteId: string; pageUrl: string }) {
  const [data, setData] = useState<Awaited<ReturnType<typeof api.getInsights>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setData(null);
    setError(null);
    api.getInsights(websiteId, pageUrl).then(setData).catch((e) => setError(e.message));
  }, [websiteId, pageUrl]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!data) return <p className="text-sm text-slate-500">Loading...</p>;

  return (
    <div className="grid sm:grid-cols-3 gap-6">
      <ScoreGauge score={data.seo_score ?? 0} label="SEO Health Score" />
      <MetricCard
        label="CTA click rate"
        value={`${data.cta_click_rate_pct}%`}
        hint="Sessions that interacted with the primary CTA"
      />
      <MetricCard
        label="Search CTR"
        value={data.search ? `${(data.search.ctr * 100).toFixed(2)}%` : "n/a"}
        hint={data.search ? `Avg. position ${data.search.avg_position}` : "No Search Console data yet"}
      />
      <div className="sm:col-span-3">
        <InsightsList insights={data.insights} />
      </div>
    </div>
  );
}

function TechnicalTab({ websiteId, pageUrl }: { websiteId: string; pageUrl: string }) {
  const [urls, setUrls] = useState(pageUrl);
  const [results, setResults] = useState<CrawlResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.latestCrawl(websiteId).then(setResults).catch(() => {});
  }, [websiteId]);

  async function runCrawl() {
    setLoading(true);
    try {
      const urlList = urls.split("\n").map((u) => u.trim()).filter(Boolean);
      const fresh = await api.runCrawl(websiteId, urlList);
      setResults((prev) => [...fresh, ...prev]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <p className="text-sm font-medium text-ink mb-2">Crawl URLs (one per line)</p>
        <textarea
          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm h-24"
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
        />
        <button className="btn-primary text-sm mt-3" onClick={runCrawl} disabled={loading}>
          {loading ? "Crawling..." : "Run crawl"}
        </button>
      </div>

      <div className="space-y-4">
        {results.map((r) => (
          <div key={r.id} className="card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-ink break-all">{r.url}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {r.title || "No title"} &middot; {r.word_count ?? 0} words &middot; status {r.status_code ?? "n/a"}
                </p>
              </div>
              <div className="text-2xl font-semibold" style={{ color: (r.seo_score ?? 0) >= 80 ? "#16a34a" : (r.seo_score ?? 0) >= 50 ? "#d97706" : "#dc2626" }}>
                {r.seo_score ?? "-"}
              </div>
            </div>
            {r.issues.length > 0 && (
              <div className="mt-3 space-y-1">
                {r.issues.map((issue, i) => (
                  <div key={i} className={`text-xs border rounded px-2 py-1 ${severityColor[issue.severity]}`}>
                    {issue.message}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {results.length === 0 && <p className="text-sm text-slate-500">No crawls yet, run one above.</p>}
      </div>
    </div>
  );
}

function BehaviourTab({ websiteId, pageUrl }: { websiteId: string; pageUrl: string }) {
  const [data, setData] = useState<HeatmapData | null>(null);

  useEffect(() => {
    setData(null);
    api.getHeatmap(websiteId, pageUrl).then(setData).catch(() => {});
  }, [websiteId, pageUrl]);

  if (!data) return <p className="text-sm text-slate-500">Loading...</p>;

  return (
    <div className="grid sm:grid-cols-2 gap-6">
      <Heatmap cells={data.click_grid} />
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <MetricCard label="Avg. scroll depth" value={`${data.scroll.avg_scroll_depth_pct}%`} hint={`${data.scroll.sessions} sessions`} />
          <MetricCard label="CTA click rate" value={`${data.cta_click_rate_pct}%`} />
        </div>
        {data.section_engagement.length > 0 && (
          <BarChart
            title="Content engagement by section"
            labels={data.section_engagement.map((s) => s.section_id)}
            values={data.section_engagement.map((s) => s.view_rate_pct)}
          />
        )}
      </div>
    </div>
  );
}

function SearchTab({ websiteId }: { websiteId: string }) {
  const [gsc, setGsc] = useState<SearchRow[]>([]);
  const [ga4, setGa4] = useState<{ page_url: string; sessions: number; conversions: number }[]>([]);

  useEffect(() => {
    api.getSearchConsole(websiteId).then(setGsc).catch(() => {});
    api.getGa4(websiteId).then(setGa4).catch(() => {});
  }, [websiteId]);

  return (
    <div className="space-y-6">
      <div className="card overflow-x-auto">
        <p className="text-sm font-medium text-ink mb-3">Search Console (last 28 days)</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-500 border-b border-slate-200">
              <th className="pb-2 pr-4">Page</th>
              <th className="pb-2 pr-4">Impressions</th>
              <th className="pb-2 pr-4">Clicks</th>
              <th className="pb-2 pr-4">CTR</th>
              <th className="pb-2">Avg. position</th>
            </tr>
          </thead>
          <tbody>
            {gsc.map((row, i) => (
              <tr key={i} className="border-b border-slate-100">
                <td className="py-2 pr-4 break-all">{row.page_url}</td>
                <td className="py-2 pr-4">{row.impressions.toLocaleString()}</td>
                <td className="py-2 pr-4">{row.clicks.toLocaleString()}</td>
                <td className="py-2 pr-4">{(row.ctr * 100).toFixed(2)}%</td>
                <td className="py-2">{row.avg_position ?? "-"}</td>
              </tr>
            ))}
            {gsc.length === 0 && (
              <tr><td colSpan={5} className="py-4 text-slate-500">No crawled pages yet, run a crawl first.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card overflow-x-auto">
        <p className="text-sm font-medium text-ink mb-3">GA4 (last 28 days)</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-500 border-b border-slate-200">
              <th className="pb-2 pr-4">Page</th>
              <th className="pb-2 pr-4">Sessions</th>
              <th className="pb-2">Conversions</th>
            </tr>
          </thead>
          <tbody>
            {ga4.map((row, i) => (
              <tr key={i} className="border-b border-slate-100">
                <td className="py-2 pr-4 break-all">{row.page_url}</td>
                <td className="py-2 pr-4">{row.sessions.toLocaleString()}</td>
                <td className="py-2">{row.conversions.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function GeoTab({ websiteId }: { websiteId: string }) {
  const [brand, setBrand] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [queries, setQueries] = useState("");
  const [summary, setSummary] = useState<GeoSummary | null>(null);
  const [insight, setInsight] = useState<Insight | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.getGeoSummary(websiteId).then((res) => {
      setSummary(res.summary);
      setInsight(res.insight);
    }).catch(() => {});
  }, [websiteId]);

  async function saveAndRun() {
    setBusy(true);
    try {
      await api.createGeoConfig(websiteId, {
        brand_name: brand,
        competitors: competitors.split(",").map((c) => c.trim()).filter(Boolean),
        queries: queries.split("\n").map((q) => q.trim()).filter(Boolean),
      });
      await api.runGeoCheck(websiteId);
      const res = await api.getGeoSummary(websiteId);
      setSummary(res.summary);
      setInsight(res.insight);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="card grid sm:grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-slate-500">Brand name</label>
          <input className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" value={brand} onChange={(e) => setBrand(e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-slate-500">Competitors (comma separated)</label>
          <input className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" value={competitors} onChange={(e) => setCompetitors(e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <label className="text-xs text-slate-500">Queries (one per line, phrase them the way a real user would ask an AI assistant)</label>
          <textarea className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm h-24" value={queries} onChange={(e) => setQueries(e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          <button className="btn-primary text-sm" onClick={saveAndRun} disabled={busy || !brand || !queries}>
            {busy ? "Running..." : "Save and run visibility check"}
          </button>
          <span className="text-xs text-slate-500 ml-3">
            Uses configured AI providers, or the demo provider if none are set.
          </span>
        </div>
      </div>

      {summary && (
        <div className="grid sm:grid-cols-3 gap-6">
          <ScoreGauge score={summary.visibility_score} label="AI Visibility Score" />
          <MetricCard label="Brand mention rate" value={`${summary.brand_mention_rate}%`} />
          <MetricCard label="Competitor mention rate" value={`${summary.competitor_mention_rate}%`} />
          <MetricCard label="Citation rate" value={`${summary.citation_rate}%`} />
          <MetricCard label="Avg. mention position" value={summary.avg_mention_position ?? "n/a"} />
          <div className="card">
            <p className="text-sm font-medium text-ink mb-2">Top cited domains</p>
            <ul className="text-sm text-slate-600 space-y-1">
              {summary.top_cited_domains.map((d) => <li key={d}>{d}</li>)}
              {summary.top_cited_domains.length === 0 && <li className="text-slate-400">None yet</li>}
            </ul>
          </div>
          {insight && (
            <div className="sm:col-span-3">
              <InsightsList insights={[insight]} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
