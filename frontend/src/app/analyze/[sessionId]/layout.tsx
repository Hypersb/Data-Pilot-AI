import { AppShell } from "@/components/product/AppShell";

export default async function AnalyzeLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = await params;
  return <AppShell sessionId={sessionId}>{children}</AppShell>;
}
