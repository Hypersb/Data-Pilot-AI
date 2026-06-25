"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  ChevronDown,
  FileText,
  FlaskConical,
  GitCompare,
  LayoutDashboard,
  LineChart,
  MessageSquare,
  Search,
  Sparkles,
  Upload,
  Users,
  Wrench,
} from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { useSessionMeta } from "@/hooks/useSessionMeta";
import { cn } from "@/lib/utils";

const primaryFlow = (id: string) => [
  { href: `/analyze/${id}`, label: "Overview", icon: LayoutDashboard },
  { href: `/analyze/${id}/insights`, label: "Insights", icon: Sparkles },
  { href: `/analyze/${id}/forecast`, label: "Forecast", icon: LineChart },
  { href: `/analyze/${id}/chat`, label: "Ask Prisma", icon: MessageSquare },
  { href: `/analyze/${id}/report`, label: "Report", icon: FileText },
];

const intelligenceLinks = (id: string) => [
  { href: `/analyze/${id}/health`, label: "Data Health", icon: Activity },
  { href: `/analyze/${id}/root-cause`, label: "Root Cause", icon: Search },
  { href: `/analyze/${id}/story`, label: "Executive Summary", icon: FileText },
  { href: `/analyze/${id}/team`, label: "Analyst Team", icon: Users },
];

const advancedLinks = (id: string) => [
  { href: `/analyze/${id}/dashboard`, label: "Charts", icon: BarChart3 },
  { href: `/analyze/${id}/models`, label: "Model Arena", icon: Brain },
  { href: `/analyze/${id}/explain`, label: "Explainable AI", icon: Sparkles },
  { href: `/analyze/${id}/compare`, label: "Compare", icon: GitCompare },
  { href: `/analyze/${id}/clean`, label: "Clean Data", icon: Wrench },
  { href: `/analyze/${id}/anomalies`, label: "Anomalies", icon: Activity },
  { href: `/analyze/${id}/experiments`, label: "Experiments", icon: FlaskConical },
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
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  active: boolean;
}) {
  return (
    <Link
      href={href}
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

export function AppShell({
  sessionId,
  children,
}: {
  sessionId?: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [advancedOpen, setAdvancedOpen] = useState(false);

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

  return (
    <div className="flex h-screen bg-bg-root">
      <aside
        className="flex shrink-0 flex-col border-r border-border bg-bg-panel"
        style={{ width: "var(--sidebar-w)" }}
      >
        <div className="border-b border-border px-4 py-4">
          <Logo size="sm" href="/" showText hideTextOnMobile />
          <SidebarMeta sessionId={sessionId} />
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto p-3">
          <div>
            <p className="mb-1.5 px-2.5 text-[11px] font-medium uppercase tracking-wider text-text-faint">
              Analysis
            </p>
            <div className="space-y-0.5">
              {primaryFlow(sessionId).map((link) => (
                <NavLink
                  key={link.href}
                  {...link}
                  active={pathname === link.href}
                />
              ))}
            </div>
          </div>

          <div>
            <p className="mb-1.5 px-2.5 text-[11px] font-medium uppercase tracking-wider text-text-faint">
              Intelligence
            </p>
            <div className="space-y-0.5">
              {intelligenceLinks(sessionId).map((link) => (
                <NavLink
                  key={link.href}
                  {...link}
                  active={pathname === link.href}
                />
              ))}
            </div>
          </div>

          <div>
            <button
              type="button"
              onClick={() => setAdvancedOpen((o) => !o)}
              className="flex w-full items-center justify-between rounded-md px-2.5 py-2 text-[13px] text-text-muted hover:bg-bg-hover"
            >
              <span className="text-[11px] font-medium uppercase tracking-wider text-text-faint">
                Advanced
              </span>
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
                  />
                ))}
              </div>
            )}
          </div>
        </nav>

        <div className="border-t border-border p-3">
          <Link
            href="/upload"
            className="flex items-center gap-2 rounded-md px-2.5 py-2 text-[13px] font-medium text-text-secondary hover:bg-bg-hover"
          >
            <Upload className="h-4 w-4" aria-hidden />
            New analysis
          </Link>
        </div>
      </aside>

      <main className="flex min-h-0 min-w-0 flex-1 flex-col bg-bg-root">{children}</main>
    </div>
  );
}
