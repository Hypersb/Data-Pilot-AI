"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "prisma-onboarding-v1";

const STEPS = [
  {
    title: "Your analysis hub",
    body: "Overview shows health score, top insights, and quick paths to forecast and chat.",
  },
  {
    title: "Ask in plain English",
    body: "Use Ask Prisma for cited answers grounded in your data — no hallucinated numbers.",
  },
  {
    title: "Share with leadership",
    body: "Download an executive report or open Executive Summary for a board-ready narrative.",
  },
] as const;

export function OnboardingTour() {
  const [step, setStep] = useState<number | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      return localStorage.getItem(STORAGE_KEY) === "done" ? null : 0;
    } catch {
      return null;
    }
  });

  function dismiss() {
    try {
      localStorage.setItem(STORAGE_KEY, "done");
    } catch {
      /* ignore */
    }
    setStep(null);
  }

  function next() {
    if (step === null || step >= STEPS.length - 1) {
      dismiss();
      return;
    }
    setStep(step + 1);
  }

  if (step === null) return null;

  const current = STEPS[step];

  return (
    <div
      className="relative mb-6 rounded-lg border border-border-focus bg-bg-elevated p-5 shadow-sm"
      role="dialog"
      aria-label="Getting started"
    >
      <button
        type="button"
        onClick={dismiss}
        className="absolute right-3 top-3 rounded-md p-1 text-text-faint hover:bg-bg-hover hover:text-text-muted"
        aria-label="Dismiss tour"
      >
        <X className="size-4" />
      </button>
      <p className="type-label">
        Step {step + 1} of {STEPS.length}
      </p>
      <h3 className="type-title mt-2 text-text-primary">{current.title}</h3>
      <p className="type-caption mt-1">{current.body}</p>
      <div className="mt-4 flex items-center gap-3">
        <Button variant="primary" onClick={next}>
          {step < STEPS.length - 1 ? "Next" : "Got it"}
        </Button>
        <button
          type="button"
          onClick={dismiss}
          className="text-sm text-text-faint hover:text-text-muted"
        >
          Skip tour
        </button>
        <div className="ml-auto flex gap-1.5">
          {STEPS.map((_, i) => (
            <span
              key={i}
              className={cn(
                "size-1.5 rounded-full",
                i === step ? "bg-text-primary" : "bg-bg-hover"
              )}
              aria-hidden
            />
          ))}
        </div>
      </div>
    </div>
  );
}
