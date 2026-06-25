"use client";

import Link from "next/link";
import { use, useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  Check,
  FileText,
  LineChart,
  Loader2,
  MessageSquare,
  RefreshCw,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { getAnalysis, getHealth, isSessionExpiredError } from "@/lib/api";
import type { AnalysisResponse, HealthResponse, InsightItem } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { OnboardingTour } from "@/components/product/OnboardingTour";
import { SessionExpired } from "@/components/product/SessionExpired";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

const PIPELINE_STEPS = [
  "Profiling dataset",
  "Generating insights",
  "Scoring quality",
  "Running forecast",
] as const;

function healthTone(score: number) {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-amber-400";
  return "text-red-400";
}

function healthRingStroke(score: number) {
  if (score >= 80) return "stroke-emerald-500";
  if (score >= 60) return "stroke-amber-500";
  return "stroke-red-500";
}

function severityVariant(severity: string): "danger" | "warning" | "default" {
  if (severity === "high") return "danger";
  if (severity === "medium") return "warning";
  return "default";
}

function SectionHeader({
  id,
  title,
  href,
  linkLabel,
}: {
  id: string;
  title: string;
  href?: string;
  linkLabel?: string;
}) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">
      <h2 id={id} className="type-label">
        {title}
      </h2>
      {href && linkLabel && (
        <Link
          href={href}
          className="inline-flex items-center gap-1 text-xs text-text-muted transition-colors duration-150 hover:text-text-primary"
        >
          {linkLabel}
          <ArrowRight className="size-3" aria-hidden />
        </Link>
      )}
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-bg-root px-4 py-3 transition-colors duration-150 hover:border-border-focus">
      <p className="text-xs text-text-faint">{label}</p>
      <p className="mt-1 text-xl font-semibold tabular-nums tracking-tight sm:text-2xl">
        {value}
      </p>
    </div>
  );
}

function HealthRing({ score }: { score: number }) {
  const r = 36;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative mx-auto size-28" role="img" aria-label={`Health score ${score} out of 100`}>
      <svg className="size-full -rotate-90" viewBox="0 0 88 88" aria-hidden>
        <circle
          cx="44"
          cy="44"
          r={r}
          fill="none"
          className="stroke-border"
          strokeWidth="6"
        />
        <circle
          cx="44"
          cy="44"
          r={r}
          fill="none"
          className={cn(healthRingStroke(score), "transition-all duration-500 ease-out")}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={cn("text-3xl font-semibold tabular-nums", healthTone(score))}>
          {score}
        </span>
        <span className="text-[10px] text-text-faint">/ 100</span>
      </div>
    </div>
  );
}

function PipelineLoader({ stepIndex }: { stepIndex: number }) {
  return (
    <div
      className="mx-auto max-w-md py-12"
      role="status"
      aria-live="polite"
      aria-label="Analysis in progress"
    >
      <div className="flex items-center gap-3">
        <Loader2 className="size-4 animate-spin text-text-muted" aria-hidden />
        <p className="text-sm font-medium text-text-primary">Analyzing your dataset</p>
      </div>
      <ol className="mt-6 space-y-3">
        {PIPELINE_STEPS.map((label, i) => {
          const done = i < stepIndex;
          const active = i === stepIndex;
          return (
            <li
              key={label}
              className={cn(
                "flex items-center gap-3 text-sm transition-colors duration-200",
                done && "text-text-primary",
                active && "text-text-secondary",
                !done && !active && "text-text-faint",
              )}
            >
              <span
                className={cn(
                  "flex size-5 shrink-0 items-center justify-center rounded-full border transition-all duration-200",
                  done && "border-emerald-500/40 bg-emerald-500/10",
                  active && "border-border-focus bg-bg-elevated",
                  !done && !active && "border-border bg-transparent",
                )}
              >
                {done ? (
                  <Check className="size-3 text-emerald-400" aria-hidden />
                ) : active ? (
                  <span className="size-1.5 animate-pulse rounded-full bg-text-muted" />
                ) : null}
              </span>
              {label}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      className="mx-auto max-w-md py-16 text-center"
      role="alert"
      aria-live="assertive"
    >
      <div className="mx-auto flex size-10 items-center justify-center rounded-full border border-red-500/20 bg-red-500/10">
        <AlertCircle className="size-5 text-danger" aria-hidden />
      </div>
      <p className="mt-4 text-sm font-medium text-text-primary">Analysis failed</p>
      <p className="mt-2 text-sm text-text-muted">{message}</p>
      <Button variant="secondary" className="mt-6 gap-2" onClick={onRetry}>
        <RefreshCw className="size-4" aria-hidden />
        Try again
      </Button>
    </div>
  );
}

function InsightCard({ item }: { item: InsightItem }) {
  return (
    <article className="rounded-lg border border-border bg-bg-root p-4 transition-colors duration-150 hover:border-border-focus">
      <Badge variant={severityVariant(item.severity)} className="mb-2">
        {item.severity}
      </Badge>
      <h3 className="text-sm font-medium leading-snug text-text-primary">{item.title}</h3>
      <p className="mt-1.5 text-xs leading-relaxed text-text-muted">{item.description}</p>
    </article>
  );
}

function EmptyInsights({ sessionId }: { sessionId: string }) {
  return (
    <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center">
      <Sparkles className="mx-auto size-5 text-text-faint" aria-hidden />
      <p className="mt-3 text-sm text-text-muted">No strong patterns detected yet.</p>
      <Link
        href={`/analyze/${sessionId}/chat?bootstrap=1`}
        className="mt-3 inline-flex items-center gap-1 text-xs text-text-secondary transition-colors hover:text-text-primary"
      >
        Ask Prisma to dig deeper
        <ArrowRight className="size-3" aria-hidden />
      </Link>
    </div>
  );
}

export default function AnalysisHubPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [fetchKey, setFetchKey] = useState(0);

  const retry = useCallback(() => {
    setFetchKey((k) => k + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setSessionExpired(false);
    setData(null);
    setHealth(null);
    setStepIndex(0);

    const interval = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, PIPELINE_STEPS.length - 1));
    }, 800);

    Promise.all([
      getAnalysis(sessionId),
      getHealth(sessionId).catch(() => null),
    ])
      .then(([analysis, healthData]) => {
        if (!cancelled) {
          setData(analysis);
          setHealth(healthData);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          if (isSessionExpiredError(e)) {
            setSessionExpired(true);
          } else {
            setError(e instanceof Error ? e.message : "Analysis failed");
          }
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
          clearInterval(interval);
        }
      });

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [sessionId, fetchKey]);

  const chartKeys = data ? Object.keys(data.dashboard.chart_data).slice(0, 2) : [];
  const topInsights = data?.insights.slice(0, 3) ?? [];
  const kpis = data?.dashboard.kpis.slice(0, 4) ?? [];
  const recommendations = [
    ...((data?.dashboard.quality_alerts ?? []).slice(0, 2)),
    ...((health?.recommended_fixes ?? []).slice(0, 3).map((r) => r.replace(/_/g, " "))),
  ];

  const forecastText =
    data?.forecast_available && data.forecast
      ? data.forecast.explanation
      : data?.forecast_message;

  if (sessionExpired) {
    return <SessionExpired />;
  }

  return (
    <Panel
      wide
      title="Overview"
      description="Dataset summary, health score, insights, and recommended next steps."
      loading={false}
    >
      {loading && <PipelineLoader stepIndex={stepIndex} />}

      {!loading && error && <ErrorState message={error} onRetry={retry} />}

      {!loading && !error && data && (
        <div className="space-y-8">
          <OnboardingTour />
          <section aria-labelledby="summary-heading">
            <SectionHeader id="summary-heading" title="Dataset summary" />
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <StatTile label="Rows" value={data.profile.rows.toLocaleString()} />
              <StatTile label="Columns" value={String(data.profile.columns)} />
              <StatTile label="Quality" value={String(data.profile.quality_score)} />
              <StatTile label="Insights" value={String(data.insight_count)} />
            </div>
          </section>

          {/* Health + KPIs */}
          <div className="grid gap-4 lg:grid-cols-12">
            <section className="lg:col-span-4" aria-labelledby="health-heading">
              <Card className="h-full transition-colors duration-150 hover:border-border-focus">
                <CardContent className="flex h-full flex-col items-center justify-center py-6">
                  <SectionHeader
                    id="health-heading"
                    title="Data health"
                    href={`/analyze/${sessionId}/health`}
                    linkLabel="Data Health"
                  />
                  {health ? (
                    <HealthRing score={health.overall_score} />
                  ) : (
                    <div className="py-6 text-center">
                      <p className="text-3xl font-semibold tabular-nums text-text-faint">—</p>
                      <p className="mt-1 text-xs text-text-faint">Score unavailable</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </section>

            {kpis.length > 0 && (
              <section className="lg:col-span-8" aria-labelledby="metrics-heading">
                <Card className="h-full transition-colors duration-150 hover:border-border-focus">
                  <CardContent className="py-5">
                    <SectionHeader id="metrics-heading" title="Key metrics" />
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                      {kpis.map((k) => (
                        <StatTile
                          key={k.column}
                          label={k.label}
                          value={k.value.toLocaleString()}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </section>
            )}
          </div>

          {/* Insights + recommendations */}
          <div className="grid gap-4 lg:grid-cols-2">
            <section aria-labelledby="insights-heading">
              <Card className="h-full">
                <CardContent className="py-5">
                  <SectionHeader
                    id="insights-heading"
                    title="Key insights"
                    href={`/analyze/${sessionId}/insights`}
                    linkLabel="All insights"
                  />
                  {topInsights.length > 0 ? (
                    <div className="space-y-3">
                      {topInsights.map((item, i) => (
                        <InsightCard key={`${item.title}-${i}`} item={item} />
                      ))}
                    </div>
                  ) : (
                    <EmptyInsights sessionId={sessionId} />
                  )}
                </CardContent>
              </Card>
            </section>

            <section aria-labelledby="recs-heading">
              <Card className="h-full">
                <CardContent className="py-5">
                  <SectionHeader id="recs-heading" title="Recommendations" />
                  {recommendations.length > 0 ? (
                    <ul className="space-y-2">
                      {recommendations.map((text, i) => (
                        <li
                          key={i}
                          className="rounded-lg border border-border bg-bg-root px-4 py-3 text-sm leading-relaxed text-text-secondary transition-colors duration-150 hover:border-border-focus"
                        >
                          {text}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center">
                      <TrendingUp className="mx-auto size-5 text-text-faint" aria-hidden />
                      <p className="mt-3 text-sm text-text-muted">
                        Data quality looks solid — no urgent fixes.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </section>
          </div>

          {/* Charts */}
          {chartKeys.length > 0 && (
            <section aria-labelledby="charts-heading">
              <SectionHeader
                id="charts-heading"
                title="Charts"
                href={`/analyze/${sessionId}/dashboard`}
                linkLabel="All charts"
              />
              <div className="grid gap-4 lg:grid-cols-2">
                {chartKeys.map((key) => (
                  <Card
                    key={key}
                    className="overflow-hidden transition-colors duration-150 hover:border-border-focus"
                  >
                    <CardContent className="p-3 sm:p-4">
                      <ChartEmbed
                        figure={data.dashboard.chart_data[key] as Record<string, unknown>}
                      />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          )}

          {/* Forecast */}
          <section aria-labelledby="forecast-heading">
            <Card className="transition-colors duration-150 hover:border-border-focus">
              <CardContent className="flex flex-col gap-4 py-5 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0 flex-1">
                  <div className="mb-2 flex items-center gap-2">
                    <LineChart className="size-4 shrink-0 text-text-faint" aria-hidden />
                    <h2 id="forecast-heading" className="type-label">
                      Forecast
                    </h2>
                  </div>
                  <p className="text-sm leading-relaxed text-text-muted">
                    {forecastText ?? "Forecast will appear when a time series is detected."}
                  </p>
                </div>
                <Link
                  href={`/analyze/${sessionId}/forecast`}
                  className="inline-flex shrink-0 items-center gap-1 text-xs text-text-muted transition-colors duration-150 hover:text-text-primary"
                >
                  View forecast
                  <ArrowRight className="size-3" aria-hidden />
                </Link>
              </CardContent>
            </Card>
          </section>

          {/* Actions */}
          <section
            className="flex flex-col gap-3 border-t border-border pt-6 sm:flex-row sm:flex-wrap"
            aria-label="Next steps"
          >
            <Button
              href={`/analyze/${sessionId}/chat?bootstrap=1`}
              variant="primary"
              className="gap-2"
            >
              <MessageSquare className="size-4" aria-hidden />
              Ask Prisma
            </Button>
            <Button href={`/analyze/${sessionId}/report`} variant="secondary" className="gap-2">
              <FileText className="size-4" aria-hidden />
              Executive report
            </Button>
            <Button href={`/analyze/${sessionId}/root-cause`} variant="ghost" className="gap-2">
              <BarChart3 className="size-4" aria-hidden />
              Root cause
            </Button>
          </section>
        </div>
      )}
    </Panel>
  );
}
