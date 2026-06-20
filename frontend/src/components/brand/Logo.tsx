import Image from "next/image";
import Link from "next/link";

const SIZES = { sm: 24, md: 32, lg: 48 } as const;

type LogoProps = {
  size?: keyof typeof SIZES;
  showText?: boolean;
  hideTextOnMobile?: boolean;
  href?: string | null;
  className?: string;
  theme?: "light" | "dark";
};

export function Logo({
  size = "md",
  showText = true,
  hideTextOnMobile = false,
  href = "/",
  className = "",
  theme = "dark",
}: LogoProps) {
  const px = SIZES[size];
  const textClass = theme === "light" ? "text-text-primary" : "text-text-primary";

  const content = (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <Image
        src="/logo.png"
        alt="Prisma AI"
        width={px}
        height={px}
        className="rounded-sm"
        priority={size === "lg"}
      />
      {showText && (
        <span
          className={`text-[15px] font-semibold tracking-tight ${textClass} ${
            hideTextOnMobile ? "hidden md:inline" : ""
          }`}
        >
          Prisma
        </span>
      )}
    </span>
  );

  if (href) {
    return (
      <Link href={href} className="inline-flex shrink-0">
        {content}
      </Link>
    );
  }

  return content;
}

export function BrandMark({
  size = 18,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  return (
    <Image
      src="/logo.png"
      alt=""
      width={size}
      height={size}
      className={`rounded-sm ${className}`}
      aria-hidden
    />
  );
}
