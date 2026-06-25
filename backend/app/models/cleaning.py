from typing import Any

from pydantic import BaseModel, Field


class CleaningAuditEntry(BaseModel):
    step: int
    operation: str
    description: str
    rows_before: int
    rows_after: int
    columns_affected: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)
