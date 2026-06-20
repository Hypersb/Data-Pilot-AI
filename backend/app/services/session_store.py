from datetime import UTC, datetime, timedelta
from typing import Any
import threading

import pandas as pd

from app.config import settings


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, df: pd.DataFrame, filename: str) -> str:
        import uuid

        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        with self._lock:
            self._sessions[session_id] = {
                "df": df,
                "filename": filename,
                "created_at": now,
                "expires_at": now + timedelta(seconds=settings.session_ttl_seconds),
            }
        return session_id

    def get(self, session_id: str) -> pd.DataFrame | None:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return None
            if datetime.now(UTC) > entry["expires_at"]:
                del self._sessions[session_id]
                return None
            return entry["df"]

    def get_meta(self, session_id: str) -> dict[str, Any] | None:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return None
            if datetime.now(UTC) > entry["expires_at"]:
                del self._sessions[session_id]
                return None
            return {"filename": entry["filename"], "created_at": entry["created_at"]}

    def delete(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def _cleanup_expired(self) -> None:
        now = datetime.now(UTC)
        with self._lock:
            expired = [sid for sid, e in self._sessions.items() if now > e["expires_at"]]
            for sid in expired:
                del self._sessions[sid]


session_store = SessionStore()
