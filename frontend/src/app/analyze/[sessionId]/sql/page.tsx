"use client";

import { use, useState } from "react";
import { generateSql } from "@/lib/api";
import type { SqlResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

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
    <Panel title="SQL Generator" description="Natural language to SQL — educational reasoning, queries are not executed." loading={false}>
      <Card>
        <CardContent className="flex gap-3 py-6">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="flex-1 rounded-lg border border-border bg-bg-root px-4 py-2 text-sm"
          />
          <Button onClick={run} disabled={loading}>
            Generate
          </Button>
        </CardContent>
      </Card>
      {error && <p className="mt-4 text-sm text-danger">{error}</p>}
      {result && (
        <div className="mt-6 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Generated SQL</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="overflow-x-auto rounded-lg bg-bg-root p-4 text-sm text-text-primary">
                {result.sql}
              </pre>
            </CardContent>
          </Card>
          <p className="text-sm leading-relaxed text-text-muted">{result.explanation}</p>
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
