"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { sendChat } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import { Composer } from "@/components/product/Composer";
import { EvidenceBlock } from "@/components/product/EvidenceBlock";

const suggestions = [
  "Summarize this dataset and highlight the top 3 business insights",
  "What trends stand out?",
  "Which category performs best?",
];

const BOOTSTRAP_Q =
  "Summarize this dataset and highlight the top 3 business insights";

function ConversationInner({ sessionId }: { sessionId: string }) {
  const searchParams = useSearchParams();
  const initialQ = searchParams.get("q");
  const bootstrap = searchParams.get("bootstrap") === "1";
  const bootstrapped = useRef(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(question: string) {
    if (!question.trim() || loading) return;
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const result = await sendChat(sessionId, question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          tool_used: result.tool_used,
          confidence: result.confidence,
          citations: result.citations,
          chart_data: result.chart_data,
        },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (bootstrapped.current) return;
    const q = initialQ || (bootstrap ? BOOTSTRAP_Q : null);
    if (q) {
      bootstrapped.current = true;
      submit(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQ, bootstrap, sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const empty = messages.length === 0 && !loading;

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="content-col px-6 py-12 lg:px-8">
          {empty && (
            <div className="py-8">
              <h2 className="type-title text-text-primary">Ask Prisma</h2>
              <p className="type-caption mt-2">
                Your AI data analyst — ask questions in plain English and get cited answers.
              </p>
              <div className="mt-8 flex flex-wrap gap-2">
                {suggestions.map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => submit(q)}
                    className="rounded-full border border-border bg-bg-panel px-4 py-2.5 text-[15px] text-text-secondary transition-colors hover:border-border-focus hover:bg-bg-hover hover:text-text-primary"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-8">
            {messages.map((msg, i) => (
              <article key={i}>
                {msg.role === "user" ? (
                  <div className="flex justify-end">
                    <p className="max-w-[90%] rounded-2xl rounded-br-md bg-bg-elevated px-4 py-3 text-[15px] leading-relaxed text-text-primary">
                      {msg.content}
                    </p>
                  </div>
                ) : (
                  <div>
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <p className="type-label">Prisma</p>
                      {msg.tool_used && (
                        <span className="rounded-full bg-bg-hover px-2 py-0.5 text-[11px] text-text-faint">
                          {msg.tool_used.replace(/_/g, " ")}
                        </span>
                      )}
                      {msg.confidence != null && (
                        <span className="text-[11px] text-text-faint">
                          {Math.round(msg.confidence * 100)}% confidence
                        </span>
                      )}
                    </div>
                    <p className="type-body text-text-secondary whitespace-pre-wrap">
                      {msg.content}
                    </p>
                    <EvidenceBlock citations={msg.citations} chartData={msg.chart_data} />
                  </div>
                )}
              </article>
            ))}

            {loading && (
              <div>
                <p className="type-label mb-3">Prisma</p>
                <div className="flex gap-1.5 py-1">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="size-1.5 animate-pulse rounded-full bg-text-muted"
                      style={{ animationDelay: `${i * 150}ms` }}
                    />
                  ))}
                </div>
              </div>
            )}

            {error && (
              <p className="rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
                {error}
              </p>
            )}
            <div ref={bottomRef} />
          </div>
        </div>
      </div>

      <div className="shrink-0 border-t border-border bg-bg-panel/95 backdrop-blur-md">
        <div className="content-col px-6 py-5 lg:px-8">
          <Composer onSubmit={submit} disabled={loading} />
        </div>
      </div>
    </div>
  );
}

export function Conversation({ sessionId }: { sessionId: string }) {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center text-sm text-text-muted">
          Loading chat…
        </div>
      }
    >
      <ConversationInner sessionId={sessionId} />
    </Suspense>
  );
}
