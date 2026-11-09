"""Outcome transitions between two test reports."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from talo.core.errors import NotImplementedYetError
from talo.core.inputs import InputSpec
from talo.modules.tests_diff.reports import Outcome, ReportRecord


class ComparisonManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baseline: InputSpec
    current: InputSpec


class Finding(StrEnum):
    FIXED = "fixed"
    STILL_FAILING = "still_failing"
    REGRESSION = "regression"
    SKIPPED_UNVERIFIED = "skipped_unverified"
    MISSING_UNVERIFIED = "missing_unverified"
    # A failure on a test absent from the baseline: no passing baseline to regress from.
    NEW_FAILURE = "new_failure"
    # Open: passed -> skipped / absent should surface as coverage gaps.


class Transition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    before: Outcome | None
    after: Outcome | None
    finding: Finding


def diff(baseline: list[ReportRecord], current: list[ReportRecord]) -> list[Transition]:
    raise NotImplementedYetError("tests.diff lands in milestone 1")
