"use client";

import { use, useEffect, useState } from "react";
import { runTeamAnalysis } from "@/lib/api";
import type { TeamAnalysisResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

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
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const sections = data
    ? [
        { title: "Data Analyst", section: data.analyst_section },
        { title: "ML Engineer", section: data.ml_section },
        { title: "Business Consultant", section: data.business_section },
        { title: "QA Auditor", section: data.qa_section },
      ]
    : [];

  return (
    <Panel title="Team Analysis" description="Multi-agent perspectives on your dataset." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {data && (
        <div className="space-y-6">
          <section className="rounded-xl border border-border bg-bg-panel p-5">
            <h2 className="text-sm font-medium text-nepal-crimson">Executive Summary</h2>
            <p className="mt-3 text-sm leading-relaxed text-text-primary">{data.executive_summary}</p>
          </section>
          {sections.map(({ title, section }) => (
            <section key={title} className="rounded-xl border border-border bg-bg-panel p-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-medium text-text-primary">{title}</h2>
                <span className="text-xs text-text-faint">confidence {Math.round(section.confidence * 100)}%</span>
              </div>
              <ul className="mt-3 space-y-2">
                {section.findings.map((f, i) => (
                  <li key={i} className="text-sm text-text-muted">• {f}</li>
                ))}
              </ul>
            </section>
          ))}
          <section>
            <h2 className="text-sm font-medium text-text-primary">Combined Recommendations</h2>
            <ul className="mt-3 space-y-2">
              {data.combined_recommendations.map((r, i) => (
                <li key={i} className="text-sm text-text-primary">• {r}</li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </Panel>
  );
}
