"use client";

import { use, useEffect, useState } from "react";
import { getStory } from "@/lib/api";
import type { StoryResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

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
      .then((d) => { if (!cancelled) setStory(d); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const sections = story
    ? [
        { title: "What happened?", body: story.what_happened },
        { title: "Why did it happen?", body: story.why_it_happened },
        { title: "What should be done next?", body: story.what_to_do_next },
      ]
    : [];

  return (
    <Panel title="Executive Story" description="What happened, why, and recommended actions." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {story && (
        <div className="space-y-6">
          {sections.map((s) => (
            <section key={s.title} className="rounded-xl border border-border bg-bg-panel p-5">
              <h2 className="text-sm font-medium text-nepal-crimson">{s.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-text-primary">{s.body}</p>
            </section>
          ))}
          {story.facts.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Grounded facts</h2>
              <ul className="mt-3 space-y-2">
                {story.facts.map((f, i) => (
                  <li key={i} className="text-sm text-text-muted">• {f}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
