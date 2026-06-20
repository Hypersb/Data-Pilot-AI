import { redirect } from "next/navigation";

export default async function AnalyzeIndex({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = await params;
  redirect(`/analyze/${sessionId}/chat`);
}
