"""Test report readers. Synthetic JSON first, JUnit XML next."""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from talo.core.errors import NotImplementedYetError


class Outcome(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ReportRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    outcome: Outcome


def load_json_report(path: Path) -> list[ReportRecord]:
    """Read a JSON array of records. Duplicate IDs are rejected as ambiguous."""
    raise NotImplementedYetError("JSON report reader lands in milestone 1")


def load_junit_report(path: Path) -> list[ReportRecord]:
    """Read JUnit XML and normalise test IDs (parameterised tests, class and file prefixes)."""
    raise NotImplementedYetError("JUnit XML reader lands in milestone 1")
