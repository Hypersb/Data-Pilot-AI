import json
import threading
from pathlib import Path
from typing import Any

from app.models.experiment import ExperimentRecord

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_STORE_FILE = _DATA_DIR / "experiments.json"


class ExperimentTracker:
    def __init__(self, store_path: Path | None = None) -> None:
        self._lock = threading.Lock()
        self._store_file = store_path or _STORE_FILE
        self._data_dir = self._store_file.parent
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if not self._store_file.exists():
            self._store_file.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict[str, Any]]:
        with self._lock:
            return json.loads(self._store_file.read_text(encoding="utf-8"))

    def _save(self, records: list[dict[str, Any]]) -> None:
        with self._lock:
            self._store_file.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def log_run(
        self,
        session_id: str,
        model_name: str,
        task_type: str,
        hyperparameters: dict[str, Any] | None = None,
        metrics: dict[str, float] | None = None,
        notes: str = "",
    ) -> str:
        record = ExperimentRecord(
            session_id=session_id,
            model_name=model_name,
            task_type=task_type,
            hyperparameters=hyperparameters or {},
            metrics=metrics or {},
            notes=notes,
        )
        records = self._load()
        records.append(record.model_dump())
        self._save(records)
        return record.run_id

    def list_runs(self, session_id: str | None = None) -> list[dict[str, Any]]:
        records = self._load()
        if session_id:
            records = [r for r in records if r.get("session_id") == session_id]
        records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return records

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        for r in self._load():
            if r.get("run_id") == run_id:
                return r
        return None


experiment_tracker = ExperimentTracker()
