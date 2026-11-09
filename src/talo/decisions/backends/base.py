"""The interface every decision backend implements."""

from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class Usage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)


class JudgeRequest(BaseModel):
    """One bounded judgment about one candidate."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    instruction: str
    text: str
    labels: list[str] = Field(min_length=1)


class JudgeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    # None means the backend abstained.
    label: str | None
    # Present only when the backend supports scores.
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    usage: Usage = Field(default_factory=Usage)

    @property
    def abstained(self) -> bool:
        return self.label is None


class DecisionBackend(Protocol):
    id: str
    remote: bool
    supports_scores: bool

    def judge(self, requests: Sequence[JudgeRequest]) -> list[JudgeResult]: ...
