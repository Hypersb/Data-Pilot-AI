export type SessionMeta = {
  filename: string;
  rows?: number;
  columns?: number;
};

const key = (sessionId: string) => `prisma:session:${sessionId}`;

export function saveSessionMeta(sessionId: string, meta: SessionMeta) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(key(sessionId), JSON.stringify(meta));
}

export function readSessionMeta(sessionId: string): SessionMeta | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(key(sessionId));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionMeta;
  } catch {
    return null;
  }
}
