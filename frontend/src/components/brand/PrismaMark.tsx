import Image from "next/image";
import { cn } from "@/lib/utils";

/** Official Prisma AI mark — sourced from brand assets */
export function PrismaMark({
  size = 32,
  className,
}: {
  size?: number;
  className?: string;
}) {
  return (
    <Image
      src="/brand/prisma-mark.png"
      alt=""
      width={size}
      height={size}
      className={cn("shrink-0 object-contain", className)}
      priority
      aria-hidden
    />
  );
}
