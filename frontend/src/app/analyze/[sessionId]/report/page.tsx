"use client";

import { use, useEffect, useState } from "react";
import { getReportV2 } from "@/lib/api";
import type { ReportV2Response } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

export default function ReportPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [report, setReport] = useState<ReportV2Response | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getReportV2(sessionId, "markdown")
      .then((d) => { if (!cancelled) setReport(d as ReportV2Response); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const download = async (format: "pdf" | "pptx") => {
    const blob = (await getReportV2(sessionId, format)) as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Panel title="Executive Report" description="Summary, findings, risks, and recommendations." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {report && (
        <div className="space-y-6">
          <div className="flex gap-3">
            <button type="button" onClick={() => download("pdf")} className="rounded-lg border border-border px-4 py-2 text-sm">
              Download PDF
            </button>
            <button type="button" onClick={() => download("pptx")} className="rounded-lg border border-border px-4 py-2 text-sm">
              Download PowerPoint
            </button>
          </div>
          <section className="rounded-xl border border-border bg-bg-panel p-5">
            <h2 className="text-sm font-medium text-nepal-crimson">Executive Summary</h2>
            <p className="mt-3 text-sm leading-relaxed text-text-primary">{report.executive_summary}</p>
          </section>
          {[
            { title: "Key Findings", items: report.key_findings },
            { title: "Risks", items: report.risks },
            { title: "Opportunities", items: report.opportunities },
            { title: "Recommendations", items: report.recommendations },
          ].map((s) => (
            <section key={s.title}>
              <h2 className="text-sm font-medium text-text-primary">{s.title}</h2>
              <ul className="mt-3 space-y-2">
                {(s.items.length ? s.items : ["None identified."]).map((item, i) => (
                  <li key={i} className="text-sm text-text-muted">• {item}</li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </Panel>
  );
}
