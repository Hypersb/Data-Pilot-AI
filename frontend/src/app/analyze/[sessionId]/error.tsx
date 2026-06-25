"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function AnalyzeError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <h1 className="type-title text-text-primary">Analysis error</h1>
      <p className="type-body mt-3 max-w-md text-text-muted">
        This page failed to load. Your session may still be valid — try again or return to the overview.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Button variant="primary" onClick={reset}>
          Try again
        </Button>
        <Button href="/upload" variant="secondary">
          New analysis
        </Button>
      </div>
    </div>
  );
}
