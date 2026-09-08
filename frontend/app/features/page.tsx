const sections = [
  {
    title: "Technical SEO crawler",
    points: [
      "Titles, meta descriptions, H1s, canonicals and robots directives",
      "Broken links, thin content and missing structured data",
      "Response time and a 0-100 SEO Health Score per page, with the scoring rules documented, not hidden",
    ],
  },
  {
    title: "Behaviour analytics",
    points: [
      "Click and scroll heatmaps from a single lightweight JS snippet",
      "Content engagement by section, mark any block with data-slai-section",
      "CTA interaction rate and outbound click tracking",
      "Built with GDPR in mind: no form values, no passwords, consent-gatable",
    ],
  },
  {
    title: "Search Console & GA4",
    points: [
      "Impressions, clicks, CTR and average position per page",
      "Sessions and conversions from GA4",
      "Automatic flag when CTR underperforms the expected curve for a page's ranking position",
    ],
  },
  {
    title: "GEO / AEO visibility",
    points: [
      "Define your brand, competitors and a set of real buyer queries",
      "Runs those queries against configured AI providers (OpenAI, Anthropic, Perplexity)",
      "Tracks mention rate, mention position, sentiment and cited source domains",
      "Ships with a demo provider so the whole dashboard works with zero API keys",
    ],
  },
];

export default function FeaturesPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-semibold text-ink mb-10">Features</h1>
      <div className="space-y-10">
        {sections.map((s) => (
          <div key={s.title}>
            <h2 className="text-xl font-semibold text-ink mb-3">{s.title}</h2>
            <ul className="list-disc list-inside space-y-1 text-slate-600 text-sm">
              {s.points.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
