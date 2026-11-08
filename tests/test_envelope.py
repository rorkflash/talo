import pytest
from pydantic import ValidationError

from talo.core.envelope import RunResult, RunStatus
from talo.core.errors import BusyError


def test_design_doc_example_validates():
    result = RunResult(
        status=RunStatus.COMPLETED,
        input_count=2400,
        candidate_count=18,
        selected_count=2,
        selected_ids=["it-118", "it-205"],
        uncertain_count=1,
        uncertain_ids=["it-209"],
        result_ref="result://r104",
    )
    assert result.schema_version == 1


def test_short_id_list_requires_truncated_flag():
    with pytest.raises(ValidationError):
        RunResult(
            status="completed",
            input_count=5,
            candidate_count=5,
            selected_count=3,
            selected_ids=["a"],
        )
    RunResult(
        status="completed",
        input_count=5,
        candidate_count=5,
        selected_count=3,
        selected_ids=["a"],
        truncated=True,
    )


def test_partial_run_must_report_unprocessed():
    with pytest.raises(ValidationError):
        RunResult(status="partial", input_count=5, candidate_count=5, selected_count=0)


def test_errors_map_to_typed_responses():
    response = BusyError("queue full").to_response()
    assert (response.status, response.code, response.retryable) == ("error", "busy", True)
