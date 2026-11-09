"""Shared profile types."""

from collections.abc import Sequence
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from talo.decisions.backends.base import DecisionBackend


class Disposition(StrEnum):
    SELECTED = "selected"
    UNCERTAIN = "uncertain"
    EXCLUDED = "excluded"


class Candidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str


class ProfileResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: str
    backend: str
    dispositions: dict[str, Disposition]


class Profile(Protocol):
    id: str
    version: str

    def run(self, candidates: Sequence[Candidate], backend: DecisionBackend) -> ProfileResult: ...
