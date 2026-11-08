import pytest
from pydantic import ValidationError

from talo.core.inputs import InputSpec


@pytest.mark.parametrize("fields", [{}, {"path": "a.json", "ref": "result://r1"}])
def test_requires_exactly_one_source(fields):
    with pytest.raises(ValidationError):
        InputSpec(**fields)


def test_accepts_each_single_source():
    InputSpec(path="a.json")
    InputSpec(inline=[{"id": "x"}])
    InputSpec(ref="result://r1")
