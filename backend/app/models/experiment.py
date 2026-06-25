from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ExperimentRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    model_name: str
    task_type: str
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    notes: str = ""
