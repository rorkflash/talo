"""Module manifest: what discovery, describe and registration read about a module."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ModuleKind(StrEnum):
    # Trusted Python code shipped with Talo.
    NATIVE = "native"
    # Declarative composition of versioned operators and decision profiles.
    PIPELINE = "pipeline"


class Limits(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_input_bytes: int = Field(default=50 * 1024 * 1024, gt=0)
    max_records: int = Field(default=100_000, gt=0)
    timeout_seconds: float = Field(default=30.0, gt=0)


class ModuleManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    kind: ModuleKind
    description: str = Field(max_length=200)
    accepts: list[Literal["path", "inline", "ref"]]
    limits: Limits = Field(default_factory=Limits)
