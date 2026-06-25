import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Panel({
  title,
  description,
  loading,
  wide,
  children,
}: {
  title: string;
  description?: string;
  loading?: boolean;
  wide?: boolean;
  children?: ReactNode;
}) {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="shrink-0 border-b border-border px-6 py-5 lg:px-8">
        <div className={cn(wide ? "dashboard-col" : "content-col")}>
          <h1 className="type-title text-text-primary">{title}</h1>
          {description && <p className="type-caption mt-1.5">{description}</p>}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-6 py-6 lg:px-8 lg:py-8">
        {loading ? (
          <div className={cn(wide ? "dashboard-col" : "content-col", "space-y-4")}>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-24 skeleton rounded-lg" />
              ))}
            </div>
            <div className="h-36 skeleton rounded-lg" />
          </div>
        ) : (
          <div className={wide ? "dashboard-col" : "content-col"}>{children}</div>
        )}
      </div>
    </div>
  );
}
