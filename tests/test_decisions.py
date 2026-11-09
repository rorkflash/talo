import pytest

from talo.core.errors import RemoteNotAllowedError
from talo.decisions.backends.api import ApiBackend
from talo.decisions.backends.base import JudgeRequest
from talo.decisions.backends.fake import FakeBackend
from talo.decisions.policy import BackendPolicy, check_backend_allowed


def _request(candidate_id: str) -> JudgeRequest:
    return JudgeRequest(
        candidate_id=candidate_id, instruction="auth failure?", text="...", labels=["yes", "no"]
    )


def test_fake_backend_answers_and_abstains():
    backend = FakeBackend({"it-118": "yes"})
    first, second = backend.judge([_request("it-118"), _request("it-209")])
    assert first.label == "yes" and not first.abstained
    assert second.abstained


def test_fake_backend_rejects_label_outside_allowed_set():
    with pytest.raises(ValueError):
        FakeBackend({"it-118": "maybe"}).judge([_request("it-118")])


def test_remote_backend_requires_opt_in():
    backend = ApiBackend("example", "small-model")
    with pytest.raises(RemoteNotAllowedError):
        check_backend_allowed(backend, BackendPolicy())
    check_backend_allowed(backend, BackendPolicy(allow_remote=True))


def test_local_backends_are_always_allowed():
    check_backend_allowed(FakeBackend(), BackendPolicy())
