"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Logo } from "@/components/brand/Logo";
import { useSessionMeta } from "@/hooks/useSessionMeta";

const v3Steps = (id: string) => [
  { href: `/analyze/${id}`, label: "Overview", step: 1 },
  { href: `/analyze/${id}/insights`, label: "Insights", step: 2 },
  { href: `/analyze/${id}/forecast`, label: "Forecast", step: 3 },
  { href: `/analyze/${id}/chat`, label: "Chat", step: 4 },
  { href: `/analyze/${id}/report`, label: "Report", step: 5 },
];

const advancedLinks = (id: string) => [
  { href: `/analyze/${id}/dashboard`, label: "Dashboard" },
  { href: `/analyze/${id}/health`, label: "Health" },
  { href: `/analyze/${id}/root-cause`, label: "Root Cause" },
  { href: `/analyze/${id}/story`, label: "Story" },
  { href: `/analyze/${id}/compare`, label: "Compare" },
  { href: `/analyze/${id}/clean`, label: "Clean" },
  { href: `/analyze/${id}/sql`, label: "SQL" },
  { href: `/analyze/${id}/anomalies`, label: "Anomalies" },
  { href: `/analyze/${id}/models`, label: "Models" },
  { href: `/analyze/${id}/explain`, label: "Drivers" },
  { href: `/analyze/${id}/experiments`, label: "Experiments" },
  { href: `/analyze/${id}/team`, label: "Team Analysis" },
  { href: `/analyze/${id}/data`, label: "Legacy Overview" },
];

function SidebarMeta({ sessionId }: { sessionId: string }) {
  const { meta, loading } = useSessionMeta(sessionId);

  if (loading && !meta) {
    return (
      <div className="mt-4 space-y-2 border-t border-border pt-4">
        <div className="h-4 w-full skeleton rounded" />
        <div className="h-3 w-2/3 skeleton rounded" />
      </div>
    );
  }

  return (
    <div className="mt-4 border-t border-border pt-4">
      <p className="truncate text-sm font-medium text-text-primary">
        {meta?.filename ?? "Dataset"}
      </p>
      {meta?.rows != null && (
        <p className="mt-1 text-sm text-text-muted">
          {meta.rows.toLocaleString()} rows · {meta.columns} cols
        </p>
      )}
    </div>
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
          <div className="page-wrap flex h-16 items-center justify-between">
            <Logo size="sm" theme="dark" href="/" />
            <Link href="/" className="text-sm text-text-muted hover:text-text-secondary">
              Home
            </Link>
          </div>
        </header>
        <main className="flex flex-1 flex-col">{children}</main>
      </div>
    );
  }

  const steps = v3Steps(sessionId);
  const activeStep = steps.find((s) => pathname === s.href)?.step ?? 0;

  return (
    <div className="flex h-screen bg-bg-root">
      <aside
        className="flex shrink-0 flex-col border-r border-border bg-bg-panel"
        style={{ width: "var(--sidebar-w)" }}
      >
        <div className="border-b border-border px-4 py-4">
          <Logo size="sm" theme="dark" href="/" />
          <SidebarMeta sessionId={sessionId} />
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          <p className="mb-2 px-3 text-[11px] font-medium uppercase tracking-wider text-text-faint">
            Analysis
          </p>
          {steps.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 rounded-lg px-3 py-2.5 text-[14px] transition-colors ${
                  active
                    ? "nav-active font-medium"
                    : "text-text-muted hover:bg-bg-hover hover:text-text-secondary"
                }`}
              >
                <span
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold ${
                    active ? "bg-nepal-crimson text-white" : "bg-bg-hover text-text-faint"
                  }`}
                >
                  {link.step}
                </span>
                {link.label}
              </Link>
            );
          })}

          <div className="pt-4">
            <button
              type="button"
              onClick={() => setAdvancedOpen((o) => !o)}
              className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-[13px] text-text-muted hover:bg-bg-hover"
            >
              <span>Advanced</span>
              <span className="text-text-faint">{advancedOpen ? "−" : "+"}</span>
            </button>
            {advancedOpen && (
              <div className="mt-1 space-y-0.5 pl-2">
                {advancedLinks(sessionId).map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`block rounded-lg px-3 py-2 text-[13px] ${
                      pathname === link.href
                        ? "text-nepal-crimson"
                        : "text-text-muted hover:bg-bg-hover hover:text-text-secondary"
                    }`}
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </nav>

        {activeStep > 0 && (
          <div className="border-t border-border px-4 py-3">
            <div className="h-1.5 rounded-full bg-bg-hover">
              <div
                className="h-1.5 rounded-full bg-nepal-crimson transition-all"
                style={{ width: `${(activeStep / 5) * 100}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-text-faint">Step {activeStep} of 5</p>
          </div>
        )}

        <div className="border-t border-border p-3">
          <Link
            href="/upload"
            className="block rounded-lg px-3 py-2.5 text-sm font-medium text-nepal-crimson hover:bg-bg-hover"
          >
            New analysis
          </Link>
        </div>
      </aside>

      <main className="flex min-h-0 min-w-0 flex-1 flex-col bg-bg-root">{children}</main>
    </div>
  );
}
