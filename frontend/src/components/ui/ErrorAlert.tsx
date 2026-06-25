import { cn } from "@/lib/utils";
import { AlertCircle } from "lucide-react";
import type { ReactNode } from "react";

export function ErrorAlert({
  message,
  className,
  children,
}: {
  message: string;
  className?: string;
  children?: ReactNode;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-lg border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger",
        className
      )}
    >
      <div className="flex gap-3">
        <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden />
        <div className="min-w-0 flex-1">
          <p>{message}</p>
          {children && <div className="mt-2 text-text-muted">{children}</div>}
        </div>
      </div>
    </div>
  );
}
