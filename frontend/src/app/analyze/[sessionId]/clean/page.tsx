"use client";

import { Suspense, use, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { cleanDataset } from "@/lib/api";
import type { CleanResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

function CleanPageContent({ sessionId }: { sessionId: string }) {
  const searchParams = useSearchParams();
  const [instruction, setInstruction] = useState("");
  const [replaceInPlace, setReplaceInPlace] = useState(false);
  const [result, setResult] = useState<CleanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const q = searchParams.get("q");
    if (q) setInstruction(q);
  }, [searchParams]);

  const run = () => {
    if (!instruction.trim()) return;
    setLoading(true);
    setError(null);
    cleanDataset(sessionId, { instruction, replace_in_place: replaceInPlace })
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  };

  return (
    <Panel title="Data Cleaning" description="Natural language cleaning with audited Pandas transforms." loading={false}>
      <div className="space-y-4">
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder='e.g. "Remove duplicate customers" or "Fill missing revenue with median"'
          rows={3}
          className="w-full rounded-xl border border-border bg-bg-panel px-4 py-3 text-sm text-text-primary"
        />
        <label className="flex items-center gap-2 text-sm text-text-muted">
          <input
            type="checkbox"
            checked={replaceInPlace}
            onChange={(e) => setReplaceInPlace(e.target.checked)}
          />
          Replace current session (default: create new session)
        </label>
        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="rounded-lg bg-nepal-crimson px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          {loading ? "Cleaning…" : "Apply cleaning"}
        </button>
      </div>
      {error && <p className="mt-4 text-sm text-danger">{error}</p>}
      {result && (
        <div className="mt-6 space-y-4">
          <p className="text-sm text-text-muted">
            Health: {result.health_score_before} → {result.health_score_after}
            {result.new_session_id && ` · New session: ${result.new_session_id}`}
          </p>
          <ul className="space-y-3">
            {result.audit_trail.map((a) => (
              <li key={a.step} className="rounded-xl border border-border bg-bg-panel p-4">
                <p className="text-xs text-text-faint">Step {a.step}: {a.operation}</p>
                <p className="mt-1 text-sm text-text-primary">{a.description}</p>
                <p className="mt-1 text-xs text-text-muted">
                  Rows: {a.rows_before} → {a.rows_after}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Panel>
  );
}

export default function CleanPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  return (
    <Suspense fallback={<Panel title="Data Cleaning" loading={true} />}>
      <CleanPageContent sessionId={sessionId} />
    </Suspense>
  );
}
