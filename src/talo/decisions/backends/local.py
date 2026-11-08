"""On-machine checkpoint (milestone 2b). Loaded once by the daemon and shared across clients."""

from collections.abc import Sequence

from talo.core.errors import NotImplementedYetError
from talo.decisions.backends.base import JudgeRequest, JudgeResult


class LocalBackend:
    remote = False
    supports_scores = True

    def __init__(self, adapter: str, revision: str) -> None:
        self.adapter = adapter
        self.revision = revision
        self.id = f"local:{adapter}@{revision}"

    def judge(self, requests: Sequence[JudgeRequest]) -> list[JudgeResult]:
        raise NotImplementedYetError("local backend lands in milestone 2b")
