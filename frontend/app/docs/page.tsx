const docs = [
  { title: "README", path: "/README.md", desc: "Project overview, quick start, tech stack." },
  { title: "Architecture", path: "/docs/architecture.md", desc: "How the four modules fit together, and the roadmap." },
  { title: "API reference", path: "/docs/api-reference.md", desc: "Every endpoint, with example requests and responses." },
  { title: "GEO methodology", path: "/docs/geo-methodology.md", desc: "How AI visibility is measured and scored." },
  { title: "Privacy", path: "/docs/privacy.md", desc: "What tracker.js collects, what it never collects, GDPR notes." },
  { title: "tracker.js SDK", path: "/sdk/README.md", desc: "How to install the behaviour tracking snippet." },
];

export default function DocsPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-semibold text-ink mb-3">Documentation</h1>
      <p className="text-slate-600 mb-10">
        Full docs live in the repository so they stay versioned alongside the code.
      </p>
      <div className="space-y-4">
        {docs.map((d) => (
          <div key={d.path} className="card">
            <p className="font-medium text-ink">{d.title}</p>
            <p className="text-sm text-slate-600 mt-1">{d.desc}</p>
            <code className="text-xs text-accent2 mt-2 block">{d.path}</code>
          </div>
        ))}
      </div>
    </div>
  );
}
