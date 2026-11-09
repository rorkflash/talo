"""Hosted model over HTTP (milestone 2a). Remote: requires workspace opt-in."""

from collections.abc import Sequence

from talo.core.errors import NotImplementedYetError
from talo.decisions.backends.base import JudgeRequest, JudgeResult


class ApiBackend:
    remote = True
    # Hosted APIs may expose no token probabilities; abstain via an explicit label instead.
    supports_scores = False

    def __init__(self, provider: str, model: str, *, effort: str = "low") -> None:
        self.provider = provider
        self.model = model
        self.effort = effort
        self.id = f"api:{provider}/{model}"

    def judge(self, requests: Sequence[JudgeRequest]) -> list[JudgeResult]:
        raise NotImplementedYetError("API backend lands in milestone 2a")
