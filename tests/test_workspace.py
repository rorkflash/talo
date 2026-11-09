import pytest

from talo.core.errors import InvalidInputError, OutsideWorkspaceError
from talo.core.workspace import Workspace


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / "ws"
    root.mkdir()
    (root / "report.json").write_text("[]")
    (tmp_path / "secret.json").write_text("{}")
    return Workspace(root)


def test_resolves_file_inside_root(workspace):
    assert workspace.resolve("report.json") == workspace.root / "report.json"


@pytest.mark.parametrize("path", ["../secret.json", "/etc/hosts"])
def test_rejects_paths_outside_root(workspace, path):
    with pytest.raises(OutsideWorkspaceError):
        workspace.resolve(path)


def test_rejects_symlink_escaping_root(workspace):
    (workspace.root / "link.json").symlink_to(workspace.root.parent / "secret.json")
    with pytest.raises(OutsideWorkspaceError):
        workspace.resolve("link.json")


def test_missing_file_is_invalid_input(workspace):
    with pytest.raises(InvalidInputError):
        workspace.resolve("nope.json")
