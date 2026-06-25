import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  title: {
    default: "Prisma AI — Turn Data Into Decisions",
    template: "%s · Prisma AI",
  },
  description:
    "Prisma AI analyzes spreadsheets, uncovers hidden patterns, predicts future outcomes, and explains what to do next.",
  icons: {
    icon: [{ url: "/brand/prisma-mark.png", type: "image/png" }],
    apple: [{ url: "/brand/prisma-mark.png", type: "image/png" }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-scroll-behavior="smooth" className={`${geistSans.variable} ${geistMono.variable} h-full`}>
      <body className="min-h-full bg-bg-root text-text-primary antialiased">{children}</body>
    </html>
  );
}
