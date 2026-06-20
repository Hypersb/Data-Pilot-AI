import Link from "next/link";
import { type ButtonHTMLAttributes, type ReactNode } from "react";

type Variant = "default" | "primary" | "secondary" | "ghost";

const styles: Record<Variant, string> = {
  default:
    "rounded-lg border border-border bg-bg-elevated text-[15px] text-text-primary hover:bg-bg-hover disabled:opacity-40",
  primary:
    "rounded-lg border border-transparent bg-nepal-crimson px-5 py-2.5 text-[15px] text-white hover:bg-nepal-crimson-hover disabled:opacity-40",
  secondary:
    "rounded-lg border border-white/20 bg-white/10 px-5 py-2.5 text-[15px] text-white backdrop-blur-sm hover:bg-white/15 disabled:opacity-40",
  ghost:
    "rounded-lg border border-transparent text-[15px] text-text-muted hover:bg-bg-hover hover:text-text-primary disabled:opacity-40",
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
  const cls = `inline-flex items-center justify-center px-4 py-2 font-medium transition-colors ${styles[variant]} ${className}`;

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
