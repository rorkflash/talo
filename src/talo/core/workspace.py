"""Workspace binding. Every input path resolves inside the session's root, symlinks included."""

from pathlib import Path

from talo.core.errors import InvalidInputError, OutsideWorkspaceError


class Workspace:
    def __init__(self, root: str | Path) -> None:
        resolved = Path(root).resolve(strict=True)
        if not resolved.is_dir():
            raise InvalidInputError(f"workspace root is not a directory: {root}")
        self.root = resolved

    def resolve(self, relative: str | Path) -> Path:
        """Resolve a workspace-relative path to an existing file inside the root."""
        candidate = Path(relative)
        if candidate.is_absolute():
            raise OutsideWorkspaceError("input paths must be relative to the workspace root")
        resolved = (self.root / candidate).resolve()
        # Check containment before existence so nothing is revealed about paths outside the root.
        if not resolved.is_relative_to(self.root):
            raise OutsideWorkspaceError(f"path escapes the workspace: {relative}")
        if not resolved.is_file():
            raise InvalidInputError(f"no such file in workspace: {relative}")
        return resolved
