import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function DataTable({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("overflow-x-auto rounded-xl border border-border", className)}>
      <table className="w-full text-sm">{children}</table>
    </div>
  );
}

export function DataTableHead({ children }: { children: ReactNode }) {
  return (
    <thead className="border-b border-border bg-bg-panel text-left text-xs font-medium uppercase tracking-wide text-text-faint">
      {children}
    </thead>
  );
}

export function DataTableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-border">{children}</tbody>;
}

export function DataTableRow({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <tr className={cn("hover:bg-bg-hover/50", className)}>{children}</tr>;
}

export function DataTableCell({
  children,
  className,
  header,
}: {
  children: ReactNode;
  className?: string;
  header?: boolean;
}) {
  const Tag = header ? "th" : "td";
  return (
    <Tag
      className={cn(
        "px-4 py-3 text-text-secondary",
        header && "font-medium text-text-faint",
        className
      )}
    >
      {children}
    </Tag>
  );
}
