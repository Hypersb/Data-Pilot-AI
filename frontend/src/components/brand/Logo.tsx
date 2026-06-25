import Link from "next/link";
import { PrismaMark } from "@/components/brand/PrismaMark";
import { cn } from "@/lib/utils";

const SIZES = { sm: 24, md: 28, lg: 40 } as const;

type LogoProps = {
  size?: keyof typeof SIZES;
  showText?: boolean;
  hideTextOnMobile?: boolean;
  href?: string | null;
  className?: string;
};

export function Logo({
  size = "md",
  showText = true,
  hideTextOnMobile = false,
  href = "/",
  className = "",
}: LogoProps) {
  const px = SIZES[size];

  const content = (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <PrismaMark size={px} />
      {showText && (
        <span
          className={cn(
            "text-[15px] font-semibold tracking-tight text-text-primary",
            hideTextOnMobile && "hidden sm:inline"
          )}
        >
          Prisma AI
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

export function BrandMark({ size = 18, className = "" }: { size?: number; className?: string }) {
  return <PrismaMark size={size} className={className} />;
}
