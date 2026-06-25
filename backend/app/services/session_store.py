from datetime import UTC, datetime, timedelta
from typing import Any
import threading
import uuid

import pandas as pd

from app.config import settings


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, df: pd.DataFrame, filename: str) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        with self._lock:
            self._sessions[session_id] = {
                "df": df,
                "filename": filename,
                "created_at": now,
                "expires_at": now + timedelta(seconds=settings.session_ttl_seconds),
                "parent_session_id": None,
                "cleaning_history": [],
            }
        return session_id

    def create_from_df(
        self,
        df: pd.DataFrame,
        filename: str,
        parent_session_id: str | None = None,
        cleaning_history: list[dict[str, Any]] | None = None,
    ) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        with self._lock:
            self._sessions[session_id] = {
                "df": df.copy(),
                "filename": filename,
                "created_at": now,
                "expires_at": now + timedelta(seconds=settings.session_ttl_seconds),
                "parent_session_id": parent_session_id,
                "cleaning_history": cleaning_history or [],
            }
        return session_id

    def replace_df(self, session_id: str, df: pd.DataFrame) -> bool:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return False
            entry["df"] = df.copy()
            return True

    def append_cleaning_history(self, session_id: str, audit_entries: list[dict[str, Any]]) -> bool:
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return False
            entry["cleaning_history"].extend(audit_entries)
            return True

    def get_lineage(self, session_id: str) -> dict[str, Any] | None:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return None
            return {
                "parent_session_id": entry.get("parent_session_id"),
                "cleaning_history": entry.get("cleaning_history", []),
            }

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

    def compare_sessions(self, session_id_a: str, session_id_b: str) -> tuple[pd.DataFrame, pd.DataFrame] | None:
        df_a = self.get(session_id_a)
        df_b = self.get(session_id_b)
        if df_a is None or df_b is None:
            return None
        return df_a, df_b

    def delete(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def get_analysis_cache(self, session_id: str) -> dict[str, Any] | None:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return None
            if datetime.now(UTC) > entry["expires_at"]:
                del self._sessions[session_id]
                return None
            return entry.get("analysis_cache")

    def set_analysis_cache(self, session_id: str, data: dict[str, Any]) -> bool:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return False
            entry["analysis_cache"] = data
            return True

    def get_ml_cache(self, session_id: str, key: str) -> dict[str, Any] | None:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return None
            if datetime.now(UTC) > entry["expires_at"]:
                del self._sessions[session_id]
                return None
            caches = entry.get("ml_cache", {})
            return caches.get(key)

    def set_ml_cache(self, session_id: str, key: str, data: dict[str, Any]) -> bool:
        self._cleanup_expired()
        with self._lock:
            entry = self._sessions.get(session_id)
            if not entry:
                return False
            if "ml_cache" not in entry:
                entry["ml_cache"] = {}
            entry["ml_cache"][key] = data
            return True

    def _cleanup_expired(self) -> None:
        now = datetime.now(UTC)
        with self._lock:
            expired = [sid for sid, e in self._sessions.items() if now > e["expires_at"]]
            for sid in expired:
                del self._sessions[sid]


session_store = SessionStore()
