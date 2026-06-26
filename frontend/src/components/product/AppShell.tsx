"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  ChevronDown,
  Database,
  FileText,
  FlaskConical,
  GitCompare,
  LayoutDashboard,
  LineChart,
  Menu,
  MessageSquare,
  Search,
  Sparkles,
  Upload,
  Users,
  Wrench,
  X,
} from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { useSessionMeta } from "@/hooks/useSessionMeta";
import { cn } from "@/lib/utils";

const primaryFlow = (id: string) => [
  { href: `/analyze/${id}`, label: "Overview", icon: LayoutDashboard },
  { href: `/analyze/${id}/insights`, label: "Insights", icon: Sparkles },
  { href: `/analyze/${id}/forecast`, label: "Forecast", icon: LineChart },
  { href: `/analyze/${id}/chat`, label: "Ask Prisma", icon: MessageSquare },
  { href: `/analyze/${id}/report`, label: "Executive Report", icon: FileText },
];

const intelligenceLinks = (id: string) => [
  { href: `/analyze/${id}/health`, label: "Data Health", icon: Activity },
  { href: `/analyze/${id}/root-cause`, label: "Root Cause", icon: Search },
  { href: `/analyze/${id}/story`, label: "Executive Summary", icon: FileText },
  { href: `/analyze/${id}/team`, label: "Analyst Team", icon: Users },
];

const advancedLinks = (id: string) => [
  { href: `/analyze/${id}/dashboard`, label: "Dashboard", icon: BarChart3 },
  { href: `/analyze/${id}/models`, label: "Model Arena", icon: Brain },
  { href: `/analyze/${id}/explain`, label: "Explainable AI", icon: Sparkles },
  { href: `/analyze/${id}/compare`, label: "Compare", icon: GitCompare },
  { href: `/analyze/${id}/clean`, label: "Clean Data", icon: Wrench },
  { href: `/analyze/${id}/anomalies`, label: "Anomalies", icon: Activity },
  { href: `/analyze/${id}/experiments`, label: "Experiments", icon: FlaskConical },
  { href: `/analyze/${id}/sql`, label: "SQL Explorer", icon: Database },
];

function SidebarMeta({ sessionId }: { sessionId: string }) {
  const { meta, loading } = useSessionMeta(sessionId);

  if (loading && !meta) {
    return (
      <div className="mt-3 space-y-2">
        <div className="h-3 w-full skeleton rounded" />
        <div className="h-3 w-2/3 skeleton rounded" />
      </div>
    );
  }

  return (
    <div className="mt-3">
      <p className="truncate text-xs font-medium text-text-primary">{meta?.filename ?? "Dataset"}</p>
      {meta?.rows != null && (
        <p className="mt-0.5 text-xs text-text-faint">
          {meta.rows.toLocaleString()} rows · {meta.columns} columns
        </p>
      )}
    </div>
  );
}

function NavLink({
  href,
  label,
  icon: Icon,
  active,
  onNavigate,
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  active: boolean;
  onNavigate?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-[13px] transition-colors",
        active
          ? "nav-active font-medium text-text-primary"
          : "text-text-muted hover:bg-bg-hover hover:text-text-secondary"
      )}
    >
      <Icon className="h-4 w-4 shrink-0 opacity-70" aria-hidden />
      {label}
    </Link>
  );
}

function SidebarNav({
  sessionId,
  pathname,
  advancedOpen,
  setAdvancedOpen,
  onNavigate,
}: {
  sessionId: string;
  pathname: string;
  advancedOpen: boolean;
  setAdvancedOpen: (open: boolean) => void;
  onNavigate?: () => void;
}) {
  return (
    <nav className="flex-1 space-y-6 overflow-y-auto p-3">
      <div>
        <p className="type-label mb-1.5 px-2.5">Analysis</p>
        <div className="space-y-0.5">
          {primaryFlow(sessionId).map((link) => (
            <NavLink
              key={link.href}
              {...link}
              active={pathname === link.href}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      </div>

      <div>
        <p className="type-label mb-1.5 px-2.5">Intelligence</p>
        <div className="space-y-0.5">
          {intelligenceLinks(sessionId).map((link) => (
            <NavLink
              key={link.href}
              {...link}
              active={pathname === link.href}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      </div>

      <div>
        <button
          type="button"
          onClick={() => setAdvancedOpen(!advancedOpen)}
          className="flex w-full items-center justify-between rounded-md px-2.5 py-2 text-[13px] text-text-muted hover:bg-bg-hover"
          aria-expanded={advancedOpen}
        >
          <span className="type-label">Advanced</span>
          <ChevronDown
            className={cn("h-3.5 w-3.5 transition-transform", advancedOpen && "rotate-180")}
            aria-hidden
          />
        </button>
        {advancedOpen && (
          <div className="mt-0.5 space-y-0.5">
            {advancedLinks(sessionId).map((link) => (
              <NavLink
                key={link.href}
                {...link}
                active={pathname === link.href}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}

export function AppShell({
  sessionId,
  children,
}: {
  sessionId?: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const closeMobile = () => setMobileOpen(false);

  useEffect(() => {
    if (!mobileOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMobileOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  if (!sessionId) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-root">
        <header className="border-b border-border">
          <div className="page-wrap flex h-14 items-center justify-between">
            <Logo size="sm" href="/" />
            <Link href="/" className="text-sm text-text-muted hover:text-text-secondary">
              Home
            </Link>
          </div>
        </header>
        <main className="flex flex-1 flex-col">{children}</main>
      </div>
    );
  }

  const sidebarContent = (
    <>
      <div className="flex items-start justify-between border-b border-border px-4 py-4">
        <div className="min-w-0 flex-1">
          <Logo size="sm" href="/" showText hideTextOnMobile />
          <SidebarMeta sessionId={sessionId} />
        </div>
        <button
          type="button"
          className="ml-2 rounded-md p-1.5 text-text-muted hover:bg-bg-hover lg:hidden"
          onClick={closeMobile}
          aria-label="Close menu"
        >
          <X className="size-5" />
        </button>
      </div>

      <SidebarNav
        sessionId={sessionId}
        pathname={pathname}
        advancedOpen={advancedOpen}
        setAdvancedOpen={setAdvancedOpen}
        onNavigate={closeMobile}
      />

      <div className="border-t border-border p-3">
        <Link
          href="/upload"
          onClick={closeMobile}
          className="flex items-center gap-2 rounded-md px-2.5 py-2 text-[13px] font-medium text-text-secondary hover:bg-bg-hover"
        >
          <Upload className="h-4 w-4" aria-hidden />
          New analysis
        </Link>
      </div>
    </>
  );

  return (
    <div className="flex h-screen bg-bg-root">
      {mobileOpen && (
        <button
          type="button"
          className="sidebar-backdrop lg:hidden"
          onClick={closeMobile}
          aria-label="Close menu"
        />
      )}

      <aside
        className={cn(
          "sidebar-drawer flex shrink-0 flex-col border-r border-border bg-bg-panel lg:relative lg:translate-x-0",
          mobileOpen && "open"
        )}
        style={{ width: "var(--sidebar-w)" }}
        aria-hidden={!mobileOpen}
      >
        {sidebarContent}
      </aside>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col bg-bg-root">
        <header className="flex h-12 shrink-0 items-center gap-3 border-b border-border px-4 lg:hidden">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="rounded-md p-2 text-text-muted hover:bg-bg-hover"
            aria-label="Open menu"
          >
            <Menu className="size-5" />
          </button>
          <span className="truncate text-sm font-medium text-text-primary">Prisma AI</span>
        </header>
        <main className="flex min-h-0 min-w-0 flex-1 flex-col">{children}</main>
      </div>
    </div>
  );
}
