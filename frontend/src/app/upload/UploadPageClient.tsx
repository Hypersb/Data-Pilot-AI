"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { Database, FileSpreadsheet, Upload } from "lucide-react";
import { getSampleDatasets, loadSampleDataset, uploadFile } from "@/lib/api";
import type { SampleDatasetItem } from "@/lib/types";
import { saveSessionMeta } from "@/lib/session-meta";
import { AppShell } from "@/components/product/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";

async function uploadLocalSample() {
  const res = await fetch("/sample/sales.csv");
  const blob = await res.blob();
  return new File([blob], "sales.csv", { type: "text/csv" });
}

export default function UploadPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pendingQ = searchParams.get("q");
  const autoSample = searchParams.get("sample") === "1";
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const [samples, setSamples] = useState<SampleDatasetItem[]>([]);

  useEffect(() => {
    getSampleDatasets()
      .then((r) => setSamples(r.samples))
      .catch(() => {});
  }, []);

  const navigateToSession = useCallback(
    (sessionId: string, filename: string, rows: number, columns: number) => {
      saveSessionMeta(sessionId, { filename, rows, columns });
      if (pendingQ) {
        router.push(`/analyze/${sessionId}/chat?q=${encodeURIComponent(pendingQ)}`);
      } else {
        router.push(`/analyze/${sessionId}`);
      }
    },
    [router, pendingQ]
  );

  const processFile = useCallback(
    async (file: File) => {
      setLoading(true);
      setError(null);
      try {
        const result = await uploadFile(file);
        navigateToSession(result.session_id, result.filename, result.rows, result.columns.length);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
        setLoading(false);
      }
    },
    [navigateToSession]
  );

  const loadSample = async (sampleId: string) => {
    setLoadingSample(sampleId);
    setError(null);
    try {
      const result = await loadSampleDataset(sampleId);
      navigateToSession(result.session_id, result.filename, result.rows, result.columns.length);
    } catch {
      if (sampleId === "sales") {
        await processFile(await uploadLocalSample());
      } else {
        setError("Could not load sample dataset. Ensure the backend is running.");
        setLoadingSample(null);
      }
    }
  };

  const sampleStarted = useRef(false);

  useEffect(() => {
    if (!autoSample || sampleStarted.current) return;
    sampleStarted.current = true;
    loadSample("sales");
  }, [autoSample]);

  const onDrop = useCallback(
    async (files: File[]) => {
      const file = files[0];
      if (file) await processFile(file);
    },
    [processFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    },
    maxFiles: 1,
    disabled: loading || !!loadingSample,
  });

  return (
    <AppShell>
      <div className="mx-auto w-full max-w-4xl px-6 py-12">
        <div className="text-center">
          <h1 className="type-headline">Upload your dataset</h1>
          <p className="mt-2 text-sm text-text-muted">
            CSV or Excel · up to 25 MB · analyzed instantly
          </p>
        </div>

        {pendingQ && (
          <Card className="mt-8">
            <CardContent className="py-4">
              <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Your question</p>
              <p className="mt-2 text-sm text-text-secondary">&ldquo;{pendingQ}&rdquo;</p>
            </CardContent>
          </Card>
        )}

        <div
          {...getRootProps()}
          className={`mt-8 cursor-pointer rounded-lg border-2 border-dashed px-6 py-14 text-center transition-colors ${
            isDragActive
              ? "border-brand/40 bg-bg-hover"
              : "border-border bg-bg-panel hover:border-border-focus hover:bg-bg-elevated"
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-8 w-8 text-text-faint" aria-hidden />
          <p className="mt-4 text-sm font-medium text-text-primary">
            {loading ? "Analyzing…" : "Drop your file here"}
          </p>
          <p className="mt-1 text-xs text-text-faint">or click to browse</p>
        </div>

        {error && (
          <p className="mt-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
            {error}
          </p>
        )}

        <section className="mt-12">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-text-faint" aria-hidden />
            <h2 className="text-sm font-medium text-text-primary">Dataset Playground</h2>
          </div>
          <p className="mt-1 text-sm text-text-muted">
            Explore Prisma AI instantly — no upload required.
          </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {samples.map((sample) => (
              <Card key={sample.id} className="transition-colors hover:border-border-focus">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base">{sample.name}</CardTitle>
                    <Badge variant="outline">{sample.task_hint}</Badge>
                  </div>
                  <CardDescription>{sample.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex items-center justify-between gap-4">
                  <p className="text-xs text-text-faint">
                    {sample.rows.toLocaleString()} rows · {sample.columns} columns
                  </p>
                  <Button
                    variant="secondary"
                    className="shrink-0 text-xs"
                    disabled={!!loadingSample || loading}
                    onClick={() => loadSample(sample.id)}
                  >
                    {loadingSample === sample.id ? "Loading…" : "Load dataset"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {samples.length === 0 && (
            <div className="mt-4">
              <Button
                variant="secondary"
                disabled={loading}
                className="gap-2"
                onClick={async () => {
                  try {
                    await processFile(await uploadLocalSample());
                  } catch {
                    setError("Could not load sample file");
                  }
                }}
              >
                <FileSpreadsheet className="h-4 w-4" aria-hidden />
                Try sample dataset
              </Button>
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}
