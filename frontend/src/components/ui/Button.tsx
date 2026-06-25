import Link from "next/link";
import { type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

type Variant = "default" | "primary" | "secondary" | "ghost";

const styles: Record<Variant, string> = {
  default:
    "rounded-md border border-border bg-bg-elevated text-sm text-text-primary hover:bg-bg-hover disabled:opacity-40",
  primary:
    "rounded-md border border-transparent bg-brand px-5 py-2.5 text-sm font-medium text-brand-fg hover:bg-brand-hover disabled:opacity-40",
  secondary:
    "rounded-md border border-border bg-transparent px-5 py-2.5 text-sm font-medium text-text-primary hover:bg-bg-hover disabled:opacity-40",
  ghost:
    "rounded-md border border-transparent text-sm text-text-muted hover:bg-bg-hover hover:text-text-primary disabled:opacity-40",
};

export function Button({
  href,
  variant = "default",
  className = "",
  children,
  disabled,
  onClick,
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  href?: string;
  variant?: Variant;
  children: ReactNode;
}) {
  const cls = cn(
    "inline-flex items-center justify-center px-4 py-2 font-medium transition-colors duration-150",
    styles[variant],
    className
  );

  if (href) {
    const external = href.startsWith("http");
    if (external) {
      return (
        <a href={href} className={cls} target="_blank" rel="noreferrer">
          {children}
        </a>
      );
    }
    return (
      <Link href={href} className={cls}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" className={cls} disabled={disabled} onClick={onClick}>
      {children}
    </button>
  );
}
