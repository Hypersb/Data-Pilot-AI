"use client";

import { use, useEffect, useState } from "react";
import { Download } from "lucide-react";
import { getReportV2 } from "@/lib/api";
import type { ReportV2Response } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

export default function ReportPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [report, setReport] = useState<ReportV2Response | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getReportV2(sessionId, "markdown")
      .then((d) => { if (!cancelled) setReport(d as ReportV2Response); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const download = async (format: "pdf" | "pptx") => {
    setDownloading(format);
    try {
      const blob = (await getReportV2(sessionId, format)) as Blob;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `prisma-report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <Panel
      wide
      title="Executive Report"
      description="Consulting-grade deliverable — cover page, findings, forecasts, models, and recommendations."
      loading={loading}
    >
      {error && (
        <p className="mb-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}
      {report && (
        <div className="space-y-6">
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" className="gap-2" onClick={() => download("pdf")} disabled={!!downloading}>
              <Download className="h-4 w-4" aria-hidden />
              {downloading === "pdf" ? "Generating…" : "Download PDF"}
            </Button>
            <Button variant="secondary" className="gap-2" onClick={() => download("pptx")} disabled={!!downloading}>
              <Download className="h-4 w-4" aria-hidden />
              {downloading === "pptx" ? "Generating…" : "Download PowerPoint"}
            </Button>
          </div>
          <Card className="border-brand/20">
            <CardHeader>
              <CardTitle>Executive Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-text-secondary">{report.executive_summary}</p>
            </CardContent>
          </Card>
          {[
            { title: "Key Findings", items: report.key_findings },
            { title: "Risks", items: report.risks },
            { title: "Opportunities", items: report.opportunities },
            { title: "Recommendations", items: report.recommendations },
          ].map((s) => (
            <Card key={s.title}>
              <CardHeader>
                <CardTitle>{s.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {(s.items.length ? s.items : ["None identified."]).map((item, i) => (
                    <li key={i} className="text-sm text-text-muted">• {item}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </Panel>
  );
}
