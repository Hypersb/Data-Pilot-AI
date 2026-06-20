"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/brand/Logo";
import { Composer } from "@/components/product/Composer";
import { Button } from "@/components/ui/Button";
import { EverestBackdrop } from "@/components/landing/EverestBackdrop";

export function LandingPage() {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="relative min-h-screen bg-sky-deep">
      <header
        className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
          scrolled ? "glass-panel border-b border-white/10" : ""
        }`}
      >
        <div className="page-wrap flex h-16 items-center justify-between">
          <Logo size="sm" theme="dark" href="/" />
          <Button href="/upload" variant="primary">
            Get started
          </Button>
        </div>
      </header>

      <section className="relative min-h-[100svh] overflow-hidden">
        <EverestBackdrop />

        <div className="page-wrap relative z-10 flex min-h-[100svh] items-center py-24">
          <div className="w-full max-w-xl">
            <div className="prayer-line mb-6 w-10 rounded-full" />
            <p className="type-label text-snow-muted">Nepal · Prisma AI</p>

            <h1 className="type-display mt-4 text-text-primary">
              Above the cloud line,
              <br />
              everything makes sense.
            </h1>

            <p className="type-caption mt-5 max-w-md text-snow-muted">
              Upload your spreadsheet. Ask questions in plain English. Get answers
              grounded in your data — not guesses.
            </p>

            <div className="mt-10">
              <Composer
                tone="landing"
                size="large"
                placeholder="What do you want to know?"
                onSubmit={(q) => router.push(`/upload?q=${encodeURIComponent(q)}`)}
              />
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-3">
              <Button href="/upload" variant="secondary">
                Upload file
              </Button>
              <span className="type-caption text-text-faint">CSV or Excel</span>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 py-8">
        <div className="page-wrap flex items-center justify-between type-caption text-text-faint">
          <span>From Nepal</span>
          <Link
            href="https://github.com/Hypersb/Data-Pilot-AI"
            className="hover:text-text-muted"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </Link>
        </div>
      </footer>
    </div>
  );
}
