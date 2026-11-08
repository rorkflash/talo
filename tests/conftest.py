from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def test_fixtures() -> Path:
    return REPO_ROOT / "fixtures" / "tests"
