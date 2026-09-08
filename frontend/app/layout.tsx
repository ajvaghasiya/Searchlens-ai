import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "SearchLens AI — Organic Search & AI Visibility Intelligence",
  description:
    "Technical SEO, on-site behaviour analytics, Search Console/GA4 reporting and AI search (GEO/AEO) visibility in one dashboard.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link href="/" className="font-semibold text-lg text-ink">
              SearchLens <span className="text-accent">AI</span>
            </Link>
            <nav className="flex items-center gap-6 text-sm text-slate-600">
              <Link href="/features" className="hover:text-ink">Features</Link>
              <Link href="/pricing" className="hover:text-ink">Pricing</Link>
              <Link href="/docs" className="hover:text-ink">Docs</Link>
              <Link href="/dashboard" className="btn-primary text-sm">Open Dashboard</Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t border-slate-200 mt-24">
          <div className="max-w-6xl mx-auto px-6 py-10 text-sm text-slate-500 flex justify-between">
            <span>SearchLens AI, an open-source SEO and AI-visibility platform.</span>
            <a
              href="https://github.com/"
              className="hover:text-ink"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
          </div>
        </footer>
      </body>
    </html>
  );
}
