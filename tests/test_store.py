import pytest

from talo.core.errors import UnknownReferenceError
from talo.core.store import format_ref, parse_ref


def test_ref_round_trip():
    assert parse_ref(format_ref("r104")) == "r104"


@pytest.mark.parametrize("ref", ["r104", "result://", "result://../x", "file://r104"])
def test_rejects_malformed_refs(ref):
    with pytest.raises(UnknownReferenceError):
        parse_ref(ref)
