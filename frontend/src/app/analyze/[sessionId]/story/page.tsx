"use client";

import { use, useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { getStory } from "@/lib/api";
import type { StoryResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

export default function StoryPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getStory(sessionId)
      .then((d) => {
        if (!cancelled) setStory(d);
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

  const sections = story
    ? [
        { title: "What happened", body: story.what_happened },
        { title: "Why it happened", body: story.why_it_happened },
        { title: "Recommended actions", body: story.what_to_do_next },
      ]
    : [];

  return (
    <Panel
      wide
      title="Executive Summary"
      description="A consulting-grade narrative — readable in under two minutes for leadership."
      loading={loading}
    >
      {error && <p className="text-sm text-danger">{error}</p>}

      {story && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-xs text-text-faint">
            <FileText className="size-3.5" />
            One-click executive briefing
          </div>

          {sections.map((s) => (
            <Card key={s.title}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-brand">{s.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-text-primary">{s.body}</p>
              </CardContent>
            </Card>
          ))}

          {story.facts.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Grounded facts</h2>
              <ul className="mt-3 space-y-2">
                {story.facts.map((f, i) => (
                  <li key={i} className="text-sm text-text-muted">
                    {f}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
