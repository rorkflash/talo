"""Scripted backend for deterministic tests. No model, no network."""

from collections.abc import Mapping, Sequence

from talo.decisions.backends.base import JudgeRequest, JudgeResult


class FakeBackend:
    remote = False

    def __init__(
        self,
        answers: Mapping[str, str | None] | None = None,
        *,
        scores: Mapping[str, float] | None = None,
        backend_id: str = "fake",
    ) -> None:
        self.id = backend_id
        self.answers = dict(answers or {})
        self.scores = dict(scores) if scores is not None else None
        self.supports_scores = scores is not None
        self.calls: list[list[JudgeRequest]] = []

    def judge(self, requests: Sequence[JudgeRequest]) -> list[JudgeResult]:
        self.calls.append(list(requests))
        results = []
        for request in requests:
            # Unscripted candidates abstain.
            label = self.answers.get(request.candidate_id)
            if label is not None and label not in request.labels:
                raise ValueError(
                    f"scripted label {label!r} is not allowed for {request.candidate_id}"
                )
            score = self.scores.get(request.candidate_id) if self.scores is not None else None
            results.append(JudgeResult(candidate_id=request.candidate_id, label=label, score=score))
        return results
