"use client";

import { use, useState } from "react";
import { generateSql } from "@/lib/api";
import type { SqlResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

export default function SqlPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [question, setQuestion] = useState("Top 10 customers by revenue");
  const [result, setResult] = useState<SqlResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = () => {
    setLoading(true);
    setError(null);
    generateSql(sessionId, { question })
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  };

  return (
    <Panel title="SQL Generator" description="Educational NL→SQL reasoning. Queries are not executed." loading={false}>
      <div className="flex gap-3">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="flex-1 rounded-lg border border-border bg-bg-panel px-4 py-2 text-sm"
        />
        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="rounded-lg bg-nepal-crimson px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Generate
        </button>
      </div>
      {error && <p className="mt-4 text-sm text-danger">{error}</p>}
      {result && (
        <div className="mt-6 space-y-4">
          <pre className="overflow-x-auto rounded-xl border border-border bg-bg-panel p-4 text-sm text-text-primary">
            {result.sql}
          </pre>
          <p className="text-sm text-text-muted">{result.explanation}</p>
          {result.assumptions.length > 0 && (
            <ul className="text-xs text-text-faint">
              {result.assumptions.map((a, i) => (
                <li key={i}>• {a}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Panel>
  );
}
