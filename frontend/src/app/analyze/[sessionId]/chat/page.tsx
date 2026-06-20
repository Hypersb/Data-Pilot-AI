import { Suspense } from "react";
import { Conversation } from "@/components/product/Conversation";

export default async function ChatPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = await params;
  return (
    <Suspense fallback={null}>
      <Conversation sessionId={sessionId} />
    </Suspense>
  );
}
