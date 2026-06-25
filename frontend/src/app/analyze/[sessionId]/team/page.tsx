"use client";

import { use, useEffect, useState } from "react";
import { Briefcase, Brain, Calculator, LineChart } from "lucide-react";
import { runTeamAnalysis } from "@/lib/api";
import type { TeamAnalysisResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

const ROLES = [
  { key: "analyst_section" as const, title: "Data Analyst", icon: LineChart },
  { key: "qa_section" as const, title: "Statistician", icon: Calculator },
  { key: "ml_section" as const, title: "ML Engineer", icon: Brain },
  { key: "business_section" as const, title: "Business Consultant", icon: Briefcase },
];

export default function TeamPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<TeamAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    runTeamAnalysis(sessionId)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return (
    <Panel
      wide
      title="AI Analyst Team"
      description="Independent perspectives from specialist roles — each with distinct observations and confidence scores."
      loading={loading}
    >
      {error && <p className="text-sm text-danger">{error}</p>}

      {data && (
        <div className="space-y-6">
          <Card className="border-brand/20 bg-brand/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-brand">Executive synthesis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-text-primary">{data.executive_summary}</p>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            {ROLES.map(({ key, title, icon: Icon }) => {
              const section = data[key];
              return (
                <Card key={key}>
                  <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Icon className="size-4 text-text-muted" />
                      {title}
                    </CardTitle>
                    <span className="text-xs text-text-faint">
                      {Math.round(section.confidence * 100)}% confidence
                    </span>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {section.findings.map((f, i) => (
                        <li key={i} className="text-sm leading-relaxed text-text-muted">
                          {f}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <section>
            <h2 className="text-sm font-medium text-text-primary">Combined recommendations</h2>
            <ul className="mt-3 space-y-2">
              {data.combined_recommendations.map((r, i) => (
                <li key={i} className="rounded-lg border border-border bg-bg-panel px-4 py-3 text-sm text-text-primary">
                  {r}
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </Panel>
  );
}
