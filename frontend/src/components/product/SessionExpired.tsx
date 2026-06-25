import Link from "next/link";
import { Clock } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function SessionExpired() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <div className="flex size-12 items-center justify-center rounded-full border border-border bg-bg-panel">
        <Clock className="size-5 text-text-muted" aria-hidden />
      </div>
      <h1 className="type-title mt-6 text-text-primary">Session expired</h1>
      <p className="type-body mt-3 max-w-md text-text-muted">
        Your analysis session has ended. Upload your dataset again to continue — or try a sample dataset
        for an instant demo.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Button href="/upload" variant="primary">
          Upload dataset
        </Button>
        <Button href="/upload?sample=1" variant="secondary">
          Try sample dataset
        </Button>
      </div>
      <p className="mt-6 text-xs text-text-faint">
        <Link href="/" className="hover:text-text-muted">
          Return to home
        </Link>
      </p>
    </div>
  );
}
