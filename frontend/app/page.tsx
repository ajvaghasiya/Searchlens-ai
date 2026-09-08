import Link from "next/link";

const modules = [
  {
    title: "Technical SEO",
    body: "A built-in crawler checks titles, meta descriptions, headings, canonicals, robots directives, structured data, internal links and thin content, then rolls it into a single Health Score per page.",
  },
  {
    title: "User Behaviour",
    body: "One JS snippet collects click and scroll data and turns it into heatmaps, plus a content engagement view built for SEO: what % of visitors actually reach the section targeting your keyword.",
  },
  {
    title: "Search Console & GA4",
    body: "Pulls impressions, clicks, CTR, average position, sessions and conversions per page, and flags pages where CTR is underperforming for their ranking position.",
  },
  {
    title: "AI Search (GEO / AEO)",
    body: "Tracks how often your brand is mentioned by ChatGPT, Perplexity and other AI answer engines against a set of real buyer queries, and which third-party sites they cite as sources.",
  },
];

export default function HomePage() {
  return (
    <div>
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <h1 className="text-4xl sm:text-5xl font-semibold text-ink tracking-tight">
          Organic search and AI visibility,<br />in one dashboard.
        </h1>
        <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto">
          SearchLens AI connects technical SEO audits, on-site behaviour analytics,
          Search Console/GA4 data and AI search visibility, then tells you what
          to fix first, in plain language.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link href="/dashboard" className="btn-primary">See the demo dashboard</Link>
          <Link href="/features" className="btn-secondary">How it works</Link>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 pb-24 grid sm:grid-cols-2 gap-6">
        {modules.map((m) => (
          <div key={m.title} className="card">
            <h3 className="font-semibold text-ink mb-2">{m.title}</h3>
            <p className="text-sm text-slate-600">{m.body}</p>
          </div>
        ))}
      </section>

      <section className="bg-white border-t border-slate-200">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-semibold text-ink mb-4">Example insight</h2>
          <div className="card bg-slate-50">
            <p className="text-sm text-slate-700">
              &ldquo;The page ranks around position 7.2 and receives 64,230 impressions a month,
              but CTR is 4.4%, below what pages at that position usually get. Visitors who do
              land on the page spend a lot of time in the technical audit section, worth testing
              a title and meta description that lead with that angle.&rdquo;
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
