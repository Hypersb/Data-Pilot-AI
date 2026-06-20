import type { ReactNode } from "react";

export function Panel({
  title,
  description,
  loading,
  children,
}: {
  title: string;
  description?: string;
  loading?: boolean;
  children?: ReactNode;
}) {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="shrink-0 border-b border-border px-6 py-6 lg:px-8">
        <div className="content-col">
          <h1 className="type-title text-text-primary">{title}</h1>
          {description && <p className="type-caption mt-2">{description}</p>}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-6 py-8 lg:px-8">
        {loading ? (
          <div className="content-col space-y-4">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-24 skeleton rounded-xl" />
              ))}
            </div>
            <div className="h-36 skeleton rounded-xl" />
          </div>
        ) : (
          <div className="content-col">{children}</div>
        )}
      </div>
    </div>
  );
}
