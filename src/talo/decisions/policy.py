"""Workspace policy for which decision backends may run."""

from pydantic import BaseModel, ConfigDict

from talo.core.errors import RemoteNotAllowedError
from talo.decisions.backends.base import DecisionBackend


class BackendPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Remote backends send request data off the machine, so they are opt-in per workspace.
    allow_remote: bool = False


def check_backend_allowed(backend: DecisionBackend, policy: BackendPolicy) -> None:
    if backend.remote and not policy.allow_remote:
        raise RemoteNotAllowedError(
            f"backend {backend.id} sends data off the machine and this workspace does not allow it"
        )
