"use client";

import {
  Activity,
  BarChart3,
  ChevronRight,
  LineChart,
  Sparkles,
  TrendingDown,
} from "lucide-react";

const SIDEBAR = [
  { section: "Analysis", items: ["Overview", "Insights", "Forecast", "Models"] },
  { section: "Intelligence", items: ["Root Cause", "Anomalies", "Health"] },
] as const;

function RevenueChart() {
  const actual = [42, 48, 52, 49, 55, 58, 54, 61, 64, 60, 66, 68];
  const forecast = [68, 71, 74, 76, 78, 80];
  const all = [...actual, ...forecast];
  const max = Math.max(...all);
  const min = Math.min(...all) - 4;
  const w = 320;
  const h = 88;
  const pad = 4;

  const toX = (i: number, total: number) => pad + (i / (total - 1)) * (w - pad * 2);
  const toY = (v: number) => h - pad - ((v - min) / (max - min)) * (h - pad * 2);

  const actualPath = actual
    .map((v, i) => `${i === 0 ? "M" : "L"} ${toX(i, all.length - 1)} ${toY(v)}`)
    .join(" ");
  const forecastStart = actual.length - 1;
  const forecastPath = forecast
    .map((v, i) => {
      const idx = forecastStart + i;
      return `${i === 0 ? "M" : "L"} ${toX(idx, all.length - 1)} ${toY(v)}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-full w-full" preserveAspectRatio="none" aria-hidden>
      <defs>
        <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(99, 102, 241, 0.25)" />
          <stop offset="100%" stopColor="rgba(99, 102, 241, 0)" />
        </linearGradient>
      </defs>
      {[0, 1, 2, 3].map((i) => (
        <line
          key={i}
          x1={pad}
          y1={pad + (i * (h - pad * 2)) / 3}
          x2={w - pad}
          y2={pad + (i * (h - pad * 2)) / 3}
          stroke="rgba(255,255,255,0.04)"
          strokeWidth="1"
        />
      ))}
      <path
        d={`${actualPath} L ${toX(actual.length - 1, all.length - 1)} ${h} L ${toX(0, all.length - 1)} ${h} Z`}
        fill="url(#chartFill)"
      />
      <path d={actualPath} fill="none" stroke="#818cf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path
        d={forecastPath}
        fill="none"
        stroke="#a5b4fc"
        strokeWidth="2"
        strokeDasharray="5 4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx={toX(forecastStart, all.length - 1)} cy={toY(actual[actual.length - 1])} r="3" fill="#818cf8" />
    </svg>
  );
}

export function ProductPreview() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-border bg-bg-panel shadow-2xl shadow-black/40">
      {/* Window chrome */}
      <div className="flex items-center gap-2 border-b border-border bg-bg-root/80 px-4 py-2.5">
        <div className="flex gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
          <span className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
          <span className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
        </div>
        <span className="ml-2 text-xs text-text-faint">Prisma AI — Sales_Analytics.csv</span>
        <span className="ml-auto rounded-md border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400">
          Processed
        </span>
      </div>

      <div className="flex min-h-[420px]">
        {/* Sidebar */}
        <aside className="hidden w-44 shrink-0 border-r border-border bg-bg-root/50 p-3 sm:block">
          <p className="px-2 text-[10px] font-medium uppercase tracking-wider text-text-faint">Workspace</p>
          {SIDEBAR.map(({ section, items }) => (
            <div key={section} className="mt-4">
              <p className="px-2 text-[10px] font-medium uppercase tracking-wider text-text-faint">{section}</p>
              <ul className="mt-1 space-y-0.5">
                {items.map((item, i) => (
                  <li
                    key={item}
                    className={`flex items-center gap-2 rounded-md px-2 py-1.5 text-xs ${
                      section === "Analysis" && i === 0
                        ? "bg-bg-hover text-text-primary"
                        : "text-text-muted"
                    }`}
                  >
                    {item === "Overview" && <BarChart3 className="h-3 w-3 shrink-0" aria-hidden />}
                    {item === "Insights" && <Sparkles className="h-3 w-3 shrink-0" aria-hidden />}
                    {item === "Forecast" && <LineChart className="h-3 w-3 shrink-0" aria-hidden />}
                    {item === "Models" && <Activity className="h-3 w-3 shrink-0" aria-hidden />}
                    {item === "Root Cause" && <TrendingDown className="h-3 w-3 shrink-0" aria-hidden />}
                    {item === "Anomalies" && <Activity className="h-3 w-3 shrink-0" aria-hidden />}
                    {item === "Health" && <Activity className="h-3 w-3 shrink-0" aria-hidden />}
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </aside>

        {/* Main */}
        <div className="min-w-0 flex-1 p-4 sm:p-5">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">Sales_Analytics.csv</h3>
              <p className="text-[11px] text-text-faint">24,532 rows · 18 columns</p>
            </div>
          </div>

          {/* Metric row */}
          <div className="mt-4 grid grid-cols-2 gap-2 lg:grid-cols-4">
            {[
              { label: "Revenue", value: "$1.84M", sub: "+8.2% YoY", up: true },
              { label: "Forecast", value: "$2.06M", sub: "30-day outlook", up: true },
              { label: "Health score", value: "92", sub: "/ 100", up: null },
              { label: "Insights", value: "14", sub: "detected", up: null },
            ].map((m) => (
              <div key={m.label} className="rounded-lg border border-border bg-bg-elevated/80 px-3 py-2.5">
                <p className="text-[10px] text-text-faint">{m.label}</p>
                <p className="mt-0.5 text-lg font-semibold tabular-nums tracking-tight">{m.value}</p>
                <p className={`text-[10px] ${m.up ? "text-emerald-400" : "text-text-faint"}`}>{m.sub}</p>
              </div>
            ))}
          </div>

          {/* Chart + insight column */}
          <div className="mt-3 grid gap-3 lg:grid-cols-5">
            <div className="rounded-lg border border-border bg-bg-elevated/60 p-3 lg:col-span-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-text-secondary">Revenue overview</p>
                <div className="flex gap-3 text-[10px] text-text-faint">
                  <span className="flex items-center gap-1">
                    <span className="h-0.5 w-3 rounded bg-indigo-400" /> Actual
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="h-0.5 w-3 rounded border border-dashed border-indigo-300" /> Forecast
                  </span>
                </div>
              </div>
              <div className="mt-2 h-24">
                <RevenueChart />
              </div>
            </div>

            <div className="space-y-2 lg:col-span-2">
              <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
                <p className="text-[10px] font-medium uppercase tracking-wider text-amber-400/90">Key insight</p>
                <p className="mt-1 text-xs leading-relaxed text-text-secondary">
                  Revenue dropped <span className="font-semibold text-text-primary">12%</span> in March
                </p>
              </div>
              <div className="rounded-lg border border-border bg-bg-elevated/60 p-3">
                <p className="text-[10px] font-medium uppercase tracking-wider text-text-faint">Root cause</p>
                <p className="mt-1 text-xs leading-relaxed text-text-secondary">West region decline</p>
              </div>
              <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3">
                <p className="text-[10px] font-medium uppercase tracking-wider text-indigo-300">Recommendation</p>
                <p className="mt-1 text-xs leading-relaxed text-text-secondary">
                  Focus on customer retention in West region
                </p>
              </div>
            </div>
          </div>

          {/* Bottom bar */}
          <div className="mt-3 flex items-center justify-between rounded-lg border border-border bg-bg-root/60 px-3 py-2">
            <p className="text-[11px] text-text-muted">
              <span className="text-text-faint">AI summary ·</span> Forecast predicts 18% recovery by Q2
            </p>
            <ChevronRight className="h-3.5 w-3.5 text-text-faint" aria-hidden />
          </div>
        </div>
      </div>
    </div>
  );
}
