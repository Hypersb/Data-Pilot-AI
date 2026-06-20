import { Suspense } from "react";
import UploadPageClient from "./UploadPageClient";

export default function UploadPage() {
  return (
    <Suspense fallback={null}>
      <UploadPageClient />
    </Suspense>
  );
}
