"use client";

import { FormEvent, useState } from "react";

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 19V5m0 0l-6 6m6-6l6 6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Composer({
  placeholder = "Ask about your data…",
  onSubmit,
  size = "default",
  tone = "app",
  disabled = false,
}: {
  placeholder?: string;
  onSubmit: (value: string) => void;
  size?: "default" | "large";
  tone?: "app" | "landing";
  disabled?: boolean;
}) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const q = value.trim();
    if (!q || disabled) return;
    setValue("");
    onSubmit(q);
  }

  const shell =
    tone === "landing"
      ? `input-shell-landing ${size === "large" ? "rounded-2xl px-4 py-3.5" : "rounded-xl px-3 py-2.5"}`
      : `input-shell ${size === "large" ? "rounded-2xl px-4 py-3" : "rounded-xl px-3 py-2.5"}`;

  const sendClass =
    tone === "landing"
      ? "bg-nepal-crimson text-white hover:bg-nepal-crimson-hover"
      : "bg-nepal-crimson text-white hover:bg-nepal-crimson-hover";

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className={`flex items-end gap-2 ${shell}`}>
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          rows={size === "large" ? 2 : 1}
          disabled={disabled}
          className="max-h-40 min-h-[26px] flex-1 resize-none bg-transparent text-[15px] leading-relaxed text-text-primary outline-none placeholder:text-text-faint disabled:opacity-50"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          disabled={!value.trim() || disabled}
          aria-label="Send"
          className={`flex size-9 shrink-0 items-center justify-center rounded-lg transition-all disabled:opacity-30 ${sendClass}`}
        >
          <SendIcon />
        </button>
      </div>
    </form>
  );
}
