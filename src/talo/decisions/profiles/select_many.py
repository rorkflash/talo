"""Judge each candidate independently; zero matches is valid."""

from collections.abc import Sequence

from talo.core.errors import NotImplementedYetError
from talo.decisions.backends.base import DecisionBackend
from talo.decisions.profiles.base import Candidate, ProfileResult


class SelectManyProfile:
    id = "select_many"
    version = "0.1.0"

    def run(self, candidates: Sequence[Candidate], backend: DecisionBackend) -> ProfileResult:
        raise NotImplementedYetError("decision profiles land in milestone 2a")
