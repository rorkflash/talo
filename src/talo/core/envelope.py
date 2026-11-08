"""Versioned response envelope shared by the CLI, the MCP adapter and, later, the daemon."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = 1


class RunStatus(StrEnum):
    COMPLETED = "completed"
    # An execution budget stopped the run before every candidate was processed.
    PARTIAL = "partial"


class RunResult(BaseModel):
    """Result of `talo run` / `talo_run`.

    Counts always describe the full evaluation. ID lists may be cut for display, in which case
    `truncated` is true. Outcome uncertainty, incomplete execution and display truncation are
    reported separately and never folded into one another.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    status: RunStatus
    input_count: int = Field(ge=0)
    candidate_count: int = Field(ge=0)
    selected_count: int = Field(ge=0)
    selected_ids: list[str] = Field(default_factory=list)
    uncertain_count: int = Field(default=0, ge=0)
    uncertain_ids: list[str] = Field(default_factory=list)
    unprocessed_count: int = Field(default=0, ge=0)
    truncated: bool = False
    result_ref: str | None = None

    @model_validator(mode="after")
    def _consistent(self) -> "RunResult":
        if self.status is RunStatus.PARTIAL and self.unprocessed_count == 0:
            raise ValueError("a partial run must report unprocessed_count > 0")
        if self.status is RunStatus.COMPLETED and self.unprocessed_count:
            raise ValueError("a completed run cannot leave records unprocessed")
        for ids, count, name in (
            (self.selected_ids, self.selected_count, "selected"),
            (self.uncertain_ids, self.uncertain_count, "uncertain"),
        ):
            if len(ids) > count:
                raise ValueError(f"{name}_ids lists more IDs than {name}_count")
            if len(ids) < count and not self.truncated:
                raise ValueError(f"{name}_ids is shorter than {name}_count but truncated is false")
        return self


class ErrorResponse(BaseModel):
    """Typed error returned instead of a RunResult."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    status: Literal["error"] = "error"
    code: str
    message: str
    retryable: bool = False
