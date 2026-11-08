import json

import pytest

from talo import __version__
from talo.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_modules_list_outputs_json(capsys):
    assert main(["modules", "list"]) == 0
    modules = json.loads(capsys.readouterr().out)
    assert [m["id"] for m in modules] == ["tests.diff"]


def test_unimplemented_command_returns_typed_error(capsys):
    assert main(["run", "tests.diff", "--input", "fixtures/tests/comparison.json"]) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["code"] == "not_implemented"
    assert "not implemented" in captured.err
