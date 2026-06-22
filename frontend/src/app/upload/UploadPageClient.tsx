"use client";

import { useCallback, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { uploadFile } from "@/lib/api";
import { saveSessionMeta } from "@/lib/session-meta";
import { AppShell } from "@/components/product/AppShell";
import { Button } from "@/components/ui/Button";

async function uploadSample() {
  const res = await fetch("/sample/sales.csv");
  const blob = await res.blob();
  return new File([blob], "sales.csv", { type: "text/csv" });
}

export default function UploadPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pendingQ = searchParams.get("q");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const processFile = useCallback(
    async (file: File) => {
      setLoading(true);
      setError(null);
      try {
        const result = await uploadFile(file);
        saveSessionMeta(result.session_id, {
          filename: result.filename,
          rows: result.rows,
          columns: result.columns.length,
        });
        const q = pendingQ ? `?q=${encodeURIComponent(pendingQ)}` : "";
        router.push(`/analyze/${result.session_id}${q ? `/chat${q}` : ""}`);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
        setLoading(false);
      }
    },
    [router, pendingQ]
  );

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
    disabled: loading,
  });

  return (
    <AppShell>
      <div className="flex flex-1 items-center justify-center px-6 py-16">
        <div className="content-col w-full">
          <h1 className="type-title text-text-primary">Upload your data</h1>
          <p className="type-caption mt-2">CSV or Excel · up to 25 MB</p>

          {pendingQ && (
            <div className="mt-6 rounded-xl border border-border bg-bg-panel px-5 py-4">
              <p className="type-label">Your question</p>
              <p className="mt-2 text-[15px] text-text-secondary">&ldquo;{pendingQ}&rdquo;</p>
            </div>
          )}

          <div
            {...getRootProps()}
            className={`mt-8 cursor-pointer rounded-2xl border-2 border-dashed px-6 py-20 text-center transition-colors ${
              isDragActive
                ? "border-nepal-crimson/60 bg-bg-hover"
                : "border-border bg-bg-panel hover:border-border-focus hover:bg-bg-elevated"
            }`}
          >
            <input {...getInputProps()} />
            <p className="text-[15px] font-medium text-text-primary">
              {loading ? "Processing…" : "Drop your file here"}
            </p>
            <p className="type-caption mt-2">or click to browse</p>
          </div>

          {error && (
            <p className="mt-4 rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
              {error}
            </p>
          )}

          <div className="mt-8 flex justify-center">
            <Button
              variant="ghost"
              disabled={loading}
              onClick={async () => {
                try {
                  await processFile(await uploadSample());
                } catch {
                  setError("Could not load sample file");
                }
              }}
            >
              Try sample dataset (recommended for demos)
            </Button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
