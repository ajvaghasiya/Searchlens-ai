const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json();
}

export interface Website {
  id: string;
  domain: string;
  name: string;
  api_key: string;
  gsc_property: string | null;
  created_at: string;
}

export interface CrawlIssue {
  code: string;
  severity: "critical" | "warning" | "info";
  message: string;
}

export interface CrawlResult {
  id: string;
  url: string;
  status_code: number | null;
  seo_score: number | null;
  title: string | null;
  meta_description: string | null;
  h1_count: number | null;
  word_count: number | null;
  images_missing_alt: number | null;
  has_structured_data: boolean;
  issues: CrawlIssue[];
  crawled_at: string;
}

export interface SectionEngagement {
  section_id: string;
  views: number;
  view_rate_pct: number;
}

export interface HeatmapData {
  click_grid: { x_bucket: number; y_bucket: number; count: number }[];
  scroll: { avg_scroll_depth_pct: number; sessions: number };
  section_engagement: SectionEngagement[];
  cta_click_rate_pct: number;
}

export interface SearchRow {
  page_url: string;
  query: string | null;
  impressions: number;
  clicks: number;
  ctr: number;
  avg_position: number | null;
}

export interface GeoSummary {
  visibility_score: number;
  brand_mention_rate: number;
  competitor_mention_rate: number;
  citation_rate: number;
  avg_mention_position: number | null;
  by_provider: Record<string, { total: number; mentioned: number; mention_rate_pct: number }>;
  top_cited_domains: string[];
}

export interface Insight {
  category: string;
  severity: "info" | "opportunity" | "critical";
  message: string;
}

export const api = {
  listWebsites: () => request<Website[]>("/websites"),
  createWebsite: (payload: { domain: string; name: string; gsc_property?: string }) =>
    request<Website>("/websites", { method: "POST", body: JSON.stringify(payload) }),

  runCrawl: (websiteId: string, urls: string[]) =>
    request<CrawlResult[]>(`/websites/${websiteId}/crawl`, {
      method: "POST",
      body: JSON.stringify({ urls }),
    }),
  latestCrawl: (websiteId: string) =>
    request<CrawlResult[]>(`/websites/${websiteId}/crawl/latest`),

  getHeatmap: (websiteId: string, pageUrl: string) =>
    request<HeatmapData>(`/websites/${websiteId}/heatmap?page_url=${encodeURIComponent(pageUrl)}`),

  getSearchConsole: (websiteId: string) =>
    request<SearchRow[]>(`/websites/${websiteId}/search-console`),
  getGa4: (websiteId: string) =>
    request<{ page_url: string; sessions: number; conversions: number }[]>(`/websites/${websiteId}/ga4`),

  createGeoConfig: (websiteId: string, payload: { brand_name: string; competitors: string[]; queries: string[] }) =>
    request(`/websites/${websiteId}/geo/config`, { method: "POST", body: JSON.stringify(payload) }),
  runGeoCheck: (websiteId: string) =>
    request(`/websites/${websiteId}/geo/run`, { method: "POST" }),
  getGeoSummary: (websiteId: string) =>
    request<{ summary: GeoSummary | null; insight: Insight | null }>(`/websites/${websiteId}/geo/summary`),

  getInsights: (websiteId: string, pageUrl: string) =>
    request<{
      seo_score: number | null;
      section_engagement: SectionEngagement[];
      cta_click_rate_pct: number;
      search: SearchRow | null;
      insights: Insight[];
    }>(`/websites/${websiteId}/insights?page_url=${encodeURIComponent(pageUrl)}`),
};
