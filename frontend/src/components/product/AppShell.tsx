"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/brand/Logo";
import { useSessionMeta } from "@/hooks/useSessionMeta";

const nav = (id: string) => [
  { href: `/analyze/${id}/chat`, label: "Chat" },
  { href: `/analyze/${id}/data`, label: "Overview" },
  { href: `/analyze/${id}/forecast`, label: "Forecast" },
  { href: `/analyze/${id}/explain`, label: "Drivers" },
  { href: `/analyze/${id}/models`, label: "Models" },
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

        <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">
          {nav(sessionId).map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`block rounded-lg px-3 py-2.5 text-[15px] transition-colors ${
                  active
                    ? "nav-active font-medium"
                    : "text-text-muted hover:bg-bg-hover hover:text-text-secondary"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="space-y-1 border-t border-border p-3">
          <Link
            href="/upload"
            className="block rounded-lg px-3 py-2.5 text-sm font-medium text-nepal-crimson hover:bg-bg-hover"
          >
            New analysis
          </Link>
          <a
            href="https://github.com/Hypersb/Data-Pilot-AI"
            target="_blank"
            rel="noreferrer"
            className="block rounded-lg px-3 py-2 text-sm text-text-faint hover:bg-bg-hover hover:text-text-muted"
          >
            GitHub
          </a>
        </div>
      </aside>

      <main className="flex min-h-0 min-w-0 flex-1 flex-col bg-bg-root">{children}</main>
    </div>
  );
}
