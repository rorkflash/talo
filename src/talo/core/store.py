"""Per-workspace result storage.

Milestone 1: results published atomically as files, run metadata (module versions, input hashes,
profile, backend, model revision) in SQLite. References resolve only against the workspace that
produced them. State lives outside the workspace root; the default location is still open.
"""

import re
from pathlib import Path

from talo.core.errors import NotImplementedYetError, UnknownReferenceError
from talo.core.workspace import Workspace

REF_PREFIX = "result://"
_REF_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def format_ref(result_id: str) -> str:
    if not _REF_ID.match(result_id):
        raise ValueError(f"invalid result id: {result_id!r}")
    return f"{REF_PREFIX}{result_id}"


def parse_ref(ref: str) -> str:
    if not ref.startswith(REF_PREFIX) or not _REF_ID.match(ref[len(REF_PREFIX) :]):
        raise UnknownReferenceError(f"not a result reference: {ref!r}")
    return ref[len(REF_PREFIX) :]


class ResultStore:
    def __init__(self, workspace: Workspace, state_dir: Path) -> None:
        self.workspace = workspace
        self.state_dir = state_dir

    def publish(self, records: list[dict], metadata: dict) -> str:
        raise NotImplementedYetError("result store lands in milestone 1")

    def page(self, ref: str, *, offset: int = 0, limit: int = 50) -> list[dict]:
        raise NotImplementedYetError("result store lands in milestone 1")

    def get(self, ref: str, record_id: str) -> dict:
        raise NotImplementedYetError("result store lands in milestone 1")
