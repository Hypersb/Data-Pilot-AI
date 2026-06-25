"use client";

import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  ChevronRight,
  FileSpreadsheet,
  GitBranch,
  LineChart,
  Menu,
  MessageSquare,
  Search,
  Shield,
  Sparkles,
  TrendingUp,
  Upload,
  X,
  Zap,
} from "lucide-react";
import { ProductPreview } from "@/components/landing/ProductPreview";
import { Logo } from "@/components/brand/Logo";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

const NAV = [
  { label: "Features", href: "#features" },
  { label: "Solutions", href: "#use-cases" },
  { label: "Demo", href: "#showcase" },
  { label: "Docs", href: "https://github.com/Hypersb/Data-Pilot-AI#readme" },
] as const;

const CAPABILITIES = [
  { icon: FileSpreadsheet, label: "CSV / Excel" },
  { icon: Brain, label: "Machine Learning" },
  { icon: LineChart, label: "Forecasting" },
  { icon: Shield, label: "Data Quality" },
  { icon: Sparkles, label: "AI Insights" },
  { icon: MessageSquare, label: "Natural Language" },
] as const;

const FEATURES = [
  {
    icon: Sparkles,
    title: "AI-Powered Insights",
    description: "Automatically discover trends, opportunities, and hidden patterns across your dataset.",
  },
  {
    icon: Search,
    title: "Root Cause Analysis",
    description: "Understand why metrics changed with contribution breakdowns and dimensional attribution.",
  },
  {
    icon: TrendingUp,
    title: "Forecast Future Outcomes",
    description: "Predict what happens next with confidence intervals and model-backed projections.",
  },
  {
    icon: BarChart3,
    title: "ML Model Arena",
    description: "Compare regression and classification models, then select the best performer.",
  },
] as const;

const WORKFLOW = [
  {
    step: 1,
    title: "Upload Dataset",
    file: "sales_analytics.csv",
    detail: "24,532 rows · 18 columns",
    icon: Upload,
  },
  {
    step: 2,
    title: "Prisma Analysis",
    metrics: [
      { label: "Insights", value: "14 found" },
      { label: "Health score", value: "92" },
      { label: "Anomalies", value: "3 detected" },
    ],
    icon: Zap,
  },
  {
    step: 3,
    title: "Recommendation",
    body: "Revenue decline linked to West region performance. Forecast predicts 18% recovery. Focus on retention campaigns.",
    icon: GitBranch,
  },
] as const;

const STEPS = [
  { n: "01", title: "Upload", body: "Drop your CSV or Excel file. Schema profiling and type inference run instantly." },
  { n: "02", title: "Analyze", body: "Insights, forecasts, anomalies, and model comparisons execute in Python — not guesswork." },
  { n: "03", title: "Act", body: "Download executive reports, explore root causes, and ask questions in plain English." },
] as const;

const USE_CASES = [
  {
    title: "Data Analysts",
    example: "Profile messy exports, surface correlations, and ship stakeholder-ready reports in minutes.",
  },
  {
    title: "Researchers",
    example: "Validate hypotheses with statistical insights, anomaly detection, and reproducible ML benchmarks.",
  },
  {
    title: "Startups",
    example: "Turn product and revenue spreadsheets into forecasts and recommendations without a data team.",
  },
  {
    title: "Business Teams",
    example: "Understand period-over-period changes and get plain-English explanations of what moved the numbers.",
  },
  {
    title: "Operations Teams",
    example: "Monitor data health, catch outliers early, and track KPIs with auto-generated dashboards.",
  },
] as const;

function FadeIn({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(t);
  }, [delay]);

  return (
    <div
      className={cn(
        "transition-all duration-700 ease-out",
        visible ? "translate-y-0 opacity-100" : "translate-y-3 opacity-0",
        className
      )}
    >
      {children}
    </div>
  );
}

export function LandingPage() {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-bg-root text-text-primary">
      {/* Navbar */}
      <header
        className={cn(
          "fixed inset-x-0 top-0 z-50 transition-all duration-200",
          scrolled ? "glass-panel shadow-sm shadow-black/20" : "border-b border-transparent bg-transparent"
        )}
      >
        <div className="page-wrap flex h-14 items-center justify-between gap-6">
          <Logo size="sm" href="/" />
          <nav className="hidden items-center gap-1 md:flex" aria-label="Main">
            {NAV.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="rounded-md px-3 py-1.5 text-sm text-text-muted transition-colors hover:text-text-primary"
                {...(item.href.startsWith("http") ? { target: "_blank", rel: "noreferrer" } : {})}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="rounded-md p-2 text-text-muted hover:bg-bg-hover md:hidden"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="size-5" />
            </button>
            <Button href="/upload" variant="ghost" className="hidden sm:inline-flex text-sm">
              Get started
            </Button>
            <Button href="/upload" variant="primary" className="landing-cta gap-2 text-sm">
              <Upload className="h-3.5 w-3.5" aria-hidden />
              <span className="hidden xs:inline">Upload dataset</span>
              <span className="sm:hidden">Upload</span>
            </Button>
          </div>
        </div>
        {mobileNavOpen && (
          <>
            <button
              type="button"
              className="sidebar-backdrop md:hidden"
              onClick={() => setMobileNavOpen(false)}
              aria-label="Close menu"
            />
            <div className="fixed inset-y-0 right-0 z-50 w-72 border-l border-border bg-bg-panel p-4 md:hidden">
              <div className="flex items-center justify-between">
                <Logo size="sm" href="/" />
                <button
                  type="button"
                  onClick={() => setMobileNavOpen(false)}
                  className="rounded-md p-2 text-text-muted hover:bg-bg-hover"
                  aria-label="Close menu"
                >
                  <X className="size-5" />
                </button>
              </div>
              <nav className="mt-6 flex flex-col gap-1" aria-label="Mobile">
                {NAV.map((item) => (
                  <Link
                    key={item.label}
                    href={item.href}
                    onClick={() => setMobileNavOpen(false)}
                    className="rounded-md px-3 py-2.5 text-sm text-text-secondary hover:bg-bg-hover"
                    {...(item.href.startsWith("http") ? { target: "_blank", rel: "noreferrer" } : {})}
                  >
                    {item.label}
                  </Link>
                ))}
                <Link
                  href="/upload?sample=1"
                  onClick={() => setMobileNavOpen(false)}
                  className="mt-2 rounded-md px-3 py-2.5 text-sm font-medium text-accent-indigo"
                >
                  Try sample dataset
                </Link>
              </nav>
            </div>
          </>
        )}
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border pt-14">
        <div className="pointer-events-none absolute inset-0 landing-hero-glow" />
        <div className="pointer-events-none absolute inset-0 grid-subtle opacity-30" />
        <div className="page-wrap relative py-16 lg:py-24">
          <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
            <FadeIn>
              <div className="max-w-xl">
                <div className="mb-6 flex items-center gap-2">
                  <Logo size="sm" href={null} showText={false} />
                  <Badge variant="outline" className="border-indigo-500/30 bg-indigo-500/5 text-indigo-300">
                    AI-Powered Data Analytics
                  </Badge>
                </div>
                <h1 className="type-display text-text-primary">
                  Turn Data Into{" "}
                  <span className="landing-gradient-text">Decisions</span>
                </h1>
                <p className="mt-5 max-w-lg text-lg leading-relaxed text-text-muted">
                  Prisma AI analyzes spreadsheets, uncovers hidden patterns, predicts future outcomes,
                  and explains what to do next.
                </p>
                <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
                  <Button href="/upload" variant="primary" className="landing-cta min-w-[168px] gap-2">
                    <Upload className="h-4 w-4" aria-hidden />
                    Upload dataset
                  </Button>
                  <Button
                    variant="secondary"
                    className="min-w-[168px] gap-2"
                    onClick={() => router.push("/upload?sample=1")}
                  >
                    <FileSpreadsheet className="h-4 w-4" aria-hidden />
                    Try sample dataset
                  </Button>
                </div>
                <p className="mt-6 text-sm text-text-faint">
                  Built for analysts, researchers, startups, and modern teams.
                </p>
              </div>
            </FadeIn>

            <FadeIn delay={120} className="relative lg:pl-4">
              <div className="landing-preview-ring absolute -inset-4 rounded-2xl opacity-60 blur-2xl" />
              <ProductPreview />
            </FadeIn>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section className="border-b border-border py-10">
        <div className="page-wrap">
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-6">
            {CAPABILITIES.map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2.5 text-sm text-text-muted">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-bg-elevated">
                  <Icon className="h-4 w-4 text-text-secondary" aria-hidden />
                </div>
                <span className="font-medium text-text-secondary">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Features */}
      <section id="features" className="border-b border-border py-20 scroll-mt-20">
        <div className="page-wrap">
          <div className="mx-auto max-w-2xl text-center">
            <p className="type-label">Core capabilities</p>
            <h2 className="type-headline mt-3">Intelligence built into every analysis</h2>
            <p className="mt-3 text-text-muted">
              Production-grade analytics — from exploratory insights to model selection.
            </p>
          </div>
          <div className="mt-14 grid gap-4 sm:grid-cols-2">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <Card
                key={title}
                className="group border-border bg-bg-panel/60 transition-all duration-200 hover:border-border-focus hover:bg-bg-elevated/80"
              >
                <CardContent className="p-6">
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-bg-root transition-colors group-hover:border-indigo-500/30 group-hover:bg-indigo-500/5">
                    <Icon className="h-5 w-5 text-text-secondary group-hover:text-indigo-300" aria-hidden />
                  </div>
                  <h3 className="text-base font-semibold text-text-primary">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-muted">{description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Showcase */}
      <section id="showcase" className="border-b border-border py-20 scroll-mt-20">
        <div className="page-wrap">
          <div className="mx-auto max-w-2xl text-center">
            <p className="type-label">Product workflow</p>
            <h2 className="type-headline mt-3">From spreadsheet to strategy</h2>
          </div>
          <div className="mt-14 grid gap-6 lg:grid-cols-[1fr_auto_1fr_auto_1fr] lg:items-stretch">
            {WORKFLOW.map((item, i) => (
              <div key={item.step} className="flex items-center gap-6 lg:contents">
                <Card className="flex-1 border-border bg-bg-panel">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full border border-indigo-500/40 bg-indigo-500/10 text-xs font-semibold text-indigo-300">
                        {item.step}
                      </span>
                      <item.icon className="h-4 w-4 text-text-faint" aria-hidden />
                    </div>
                    <h3 className="mt-4 font-semibold">{item.title}</h3>
                    {"file" in item && (
                      <>
                        <p className="mt-2 font-mono text-sm text-indigo-300">{item.file}</p>
                        <p className="mt-1 text-xs text-text-faint">{item.detail}</p>
                      </>
                    )}
                    {"metrics" in item && (
                      <ul className="mt-4 space-y-2">
                        {item.metrics.map((m) => (
                          <li key={m.label} className="flex justify-between text-sm">
                            <span className="text-text-muted">{m.label}</span>
                            <span className="font-medium tabular-nums text-text-primary">{m.value}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {"body" in item && (
                      <p className="mt-4 text-sm leading-relaxed text-text-muted">{item.body}</p>
                    )}
                  </CardContent>
                </Card>
                {i < WORKFLOW.length - 1 && (
                  <div className="hidden items-center justify-center lg:flex">
                    <ChevronRight className="h-5 w-5 text-text-faint" aria-hidden />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-b border-border py-20">
        <div className="page-wrap">
          <div className="mx-auto max-w-2xl text-center">
            <p className="type-label">How it works</p>
            <h2 className="type-headline mt-3">Three steps to clarity</h2>
          </div>
          <div className="relative mt-14">
            <div className="absolute left-0 right-0 top-5 hidden h-px bg-border md:block" aria-hidden />
            <div className="grid gap-10 md:grid-cols-3">
              {STEPS.map(({ n, title, body }) => (
                <div key={title} className="relative text-center md:text-left">
                  <span className="relative z-10 inline-flex h-10 w-10 items-center justify-center rounded-full border border-border bg-bg-elevated font-mono text-xs text-text-muted">
                    {n}
                  </span>
                  <h3 className="mt-4 text-lg font-semibold">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-muted">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Use cases */}
      <section id="use-cases" className="border-b border-border py-20 scroll-mt-20">
        <div className="page-wrap">
          <div className="mx-auto max-w-2xl text-center">
            <p className="type-label">Solutions</p>
            <h2 className="type-headline mt-3">Built for teams that run on data</h2>
          </div>
          <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {USE_CASES.map(({ title, example }) => (
              <Card key={title} className="border-border bg-bg-panel/50">
                <CardContent className="p-5">
                  <h3 className="font-semibold text-text-primary">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-muted">{example}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20">
        <div className="page-wrap">
          <Card className="mx-auto max-w-3xl overflow-hidden border-border bg-bg-elevated">
            <CardContent className="relative px-8 py-12 text-center sm:px-12">
              <div className="pointer-events-none absolute inset-0 landing-hero-glow opacity-50" />
              <div className="relative">
                <Activity className="mx-auto h-8 w-8 text-indigo-400" aria-hidden />
                <h2 className="mt-4 type-headline">Start analyzing in minutes</h2>
                <p className="mx-auto mt-3 max-w-md text-sm text-text-muted">
                  Upload a dataset or try a sample. No account required. Full pipeline included.
                </p>
                <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                  <Button href="/upload" variant="primary" className="landing-cta gap-2">
                    Upload dataset
                    <ArrowRight className="h-4 w-4" aria-hidden />
                  </Button>
                  <Button variant="secondary" onClick={() => router.push("/upload?sample=1")}>
                    Try sample dataset
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="page-wrap">
          <div className="flex flex-col gap-10 lg:flex-row lg:justify-between">
            <div>
              <Logo size="sm" href="/" />
              <p className="mt-3 max-w-xs text-sm text-text-faint">
                Professional AI analytics platform for modern data teams.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
              <div>
                <p className="type-label mb-3">Product</p>
                <ul className="space-y-2 text-sm text-text-muted">
                  <li><Link href="#features" className="hover:text-text-primary">Features</Link></li>
                  <li><Link href="#showcase" className="hover:text-text-primary">Demo</Link></li>
                  <li><Link href="/upload" className="hover:text-text-primary">Upload</Link></li>
                </ul>
              </div>
              <div>
                <p className="type-label mb-3">Resources</p>
                <ul className="space-y-2 text-sm text-text-muted">
                  <li>
                    <Link href="https://github.com/Hypersb/Data-Pilot-AI#readme" target="_blank" rel="noreferrer" className="hover:text-text-primary">
                      Docs
                    </Link>
                  </li>
                  <li>
                    <Link href="https://github.com/Hypersb/Data-Pilot-AI" target="_blank" rel="noreferrer" className="hover:text-text-primary">
                      GitHub
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <p className="type-label mb-3">Legal</p>
                <ul className="space-y-2 text-sm text-text-muted">
                  <li><span className="cursor-default">Privacy</span></li>
                  <li><span className="cursor-default">Terms</span></li>
                </ul>
              </div>
            </div>
          </div>
          <p className="mt-10 border-t border-border pt-8 text-center text-xs text-text-faint">
            © {new Date().getFullYear()} Prisma AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
