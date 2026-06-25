import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-bg-root px-6 text-center">
      <Logo size="md" href="/" />
      <p className="type-display mt-10 text-text-primary">404</p>
      <h1 className="type-title mt-2 text-text-secondary">Page not found</h1>
      <p className="type-body mt-3 max-w-md text-text-muted">
        This page doesn&apos;t exist or may have moved. Start a new analysis or return home.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Button href="/upload" variant="primary">
          Upload dataset
        </Button>
        <Button href="/" variant="secondary">
          Back to home
        </Button>
      </div>
    </div>
  );
}
