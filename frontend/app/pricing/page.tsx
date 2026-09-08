const plans = [
  {
    name: "Free / Self-hosted",
    price: "€0",
    blurb: "Run it yourself with Docker Compose. No limits beyond your own infrastructure.",
    features: ["1 website", "Unlimited crawls", "Unlimited behaviour events", "Demo-mode GEO tracking"],
  },
  {
    name: "Pro (planned)",
    price: "€29/mo",
    blurb: "Hosted version with managed Postgres, background crawling and real GEO providers included.",
    features: ["5 websites", "Scheduled crawls", "GA4 + Search Console sync", "50 GEO queries/mo"],
  },
  {
    name: "Agency (planned)",
    price: "Contact us",
    blurb: "For teams managing SEO across multiple client sites.",
    features: ["Unlimited websites", "White-label reports", "Team accounts", "Priority support"],
  },
];

export default function PricingPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-semibold text-ink mb-3">Pricing</h1>
      <p className="text-slate-600 mb-10">
        SearchLens AI is open source. Self-host it for free today, hosted plans below are the
        direction the product is heading, not yet billed.
      </p>
      <div className="grid sm:grid-cols-3 gap-6">
        {plans.map((p) => (
          <div key={p.name} className="card flex flex-col">
            <h3 className="font-semibold text-ink">{p.name}</h3>
            <p className="text-2xl font-semibold text-ink mt-2">{p.price}</p>
            <p className="text-sm text-slate-600 mt-2 flex-1">{p.blurb}</p>
            <ul className="mt-4 space-y-1 text-sm text-slate-600">
              {p.features.map((f) => (
                <li key={f}>&middot; {f}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
