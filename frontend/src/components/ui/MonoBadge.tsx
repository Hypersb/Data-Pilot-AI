import type { ReactNode } from "react";

export function MonoBadge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-md bg-bg-muted px-2 py-0.5 font-mono text-[11px] text-text-secondary">
      {children}
    </span>
  );
}
