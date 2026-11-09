import json

import pytest

from talo.modules.tests_diff.diff import ComparisonManifest, Transition, diff
from talo.modules.tests_diff.reports import ReportRecord


def _records(path):
    return [ReportRecord.model_validate(r) for r in json.loads(path.read_text())]


def test_fixtures_match_contract(test_fixtures):
    ComparisonManifest.model_validate_json((test_fixtures / "comparison.json").read_text())
    _records(test_fixtures / "before.json")
    _records(test_fixtures / "after.json")
    for row in json.loads((test_fixtures / "expected_diff.json").read_text()):
        Transition.model_validate(row)


@pytest.mark.xfail(reason="tests.diff not implemented yet", strict=True)
def test_golden_transitions(test_fixtures):
    expected = [
        Transition.model_validate(row)
        for row in json.loads((test_fixtures / "expected_diff.json").read_text())
    ]
    actual = diff(_records(test_fixtures / "before.json"), _records(test_fixtures / "after.json"))
    assert sorted(actual, key=lambda t: t.id) == sorted(expected, key=lambda t: t.id)
