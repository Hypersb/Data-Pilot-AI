"use client";

import { useEffect } from "react";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/Button";

export default function GlobalError({
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
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center bg-bg-root px-6 text-center">
        <Logo size="md" href="/" />
        <h1 className="type-title mt-10 text-text-primary">Something went wrong</h1>
        <p className="type-body mt-3 max-w-md text-text-muted">
          An unexpected error occurred. Try again or start a fresh analysis.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Button variant="primary" onClick={reset}>
            Try again
          </Button>
          <Button href="/upload" variant="secondary">
            Upload dataset
          </Button>
        </div>
      </body>
    </html>
  );
}
