import json

import pytest

from talo.cli import main
from talo.core.errors import (
    BackendUnavailableError,
    InvalidInputError,
    RemoteNotAllowedError,
    UnknownModelError,
)
from talo.decisions.backends.api import ApiBackend
from talo.decisions.backends.local import LocalBackend
from talo.decisions.models import (
    ModelsConfig,
    backend_for_profile,
    load_models_config,
    load_models_config_from_env,
    models_file_path,
    select_model,
)
from talo.decisions.policy import BackendPolicy

LOCAL = {"backend": "local", "adapter": "laya", "checkpoint": "org/laya", "revision": "abc123"}
API = {"backend": "api", "provider": "anthropic", "model": "claude-haiku-5-5"}


@pytest.fixture
def config() -> ModelsConfig:
    return ModelsConfig.model_validate(
        {
            "models": {"laya": LOCAL, "haiku": API, "fake": {"backend": "fake"}},
            "profiles": {"default": "laya", "select_many": "haiku"},
        }
    )


def test_example_file_is_valid(repo_root):
    config = load_models_config(repo_root / "models.example.toml", required=True)
    assert set(config.models) == {"laya-en", "small-llm", "haiku", "dev-fake"}


@pytest.mark.parametrize(
    ("env", "override", "expected", "source"),
    [
        ({}, None, "laya", "default_config"),
        ({}, "fake", "fake", "override"),
        ({"TALO_DECISION_MODEL": "fake"}, None, "fake", "default_env"),
        (
            {"TALO_DECISION_MODEL_ROUTE": "haiku", "TALO_DECISION_MODEL": "fake"},
            None,
            "haiku",
            "profile_env",
        ),
        ({"TALO_DECISION_MODEL_ROUTE": "haiku"}, "fake", "fake", "override"),
        ({"TALO_DECISION_MODEL_ROUTE": "  "}, None, "laya", "default_config"),
    ],
)
def test_route_selection_precedence(config, env, override, expected, source):
    selection = select_model("route", config, env=env, override=override)
    assert (selection.model, selection.source) == (expected, source)


def test_profile_mapping_beats_default(config):
    selection = select_model("select_many", config, env={})
    assert (selection.model, selection.source) == ("haiku", "profile_config")


def test_env_beats_profile_mapping(config):
    selection = select_model("select_many", config, env={"TALO_DECISION_MODEL": "fake"})
    assert selection.model == "fake"


def test_env_cannot_name_undefined_model(config):
    with pytest.raises(UnknownModelError):
        select_model("route", config, env={"TALO_DECISION_MODEL": "gpt-something"})


def test_unknown_profile_is_invalid(config):
    with pytest.raises(InvalidInputError):
        select_model("summarise", config, env={})


def test_nothing_configured_is_typed_error():
    with pytest.raises(BackendUnavailableError):
        select_model("route", ModelsConfig(), env={})


def test_profiles_must_reference_defined_models():
    with pytest.raises(ValueError):
        ModelsConfig.model_validate({"models": {"laya": LOCAL}, "profiles": {"route": "nope"}})


def test_unknown_backend_fields_are_rejected():
    with pytest.raises(ValueError):
        ModelsConfig.model_validate({"models": {"laya": {**LOCAL, "api_key": "x"}}})


def test_backend_built_from_spec(config):
    _, backend = backend_for_profile("route", config, BackendPolicy(), env={})
    assert isinstance(backend, LocalBackend)
    assert backend.id == "local:laya:org/laya@abc123"


def test_env_cannot_bypass_remote_policy(config):
    env = {"TALO_DECISION_MODEL": "haiku"}
    with pytest.raises(RemoteNotAllowedError):
        backend_for_profile("route", config, BackendPolicy(), env=env)
    _, backend = backend_for_profile("route", config, BackendPolicy(allow_remote=True), env=env)
    assert isinstance(backend, ApiBackend) and backend.effort == "low"


def test_models_file_location(tmp_path):
    assert models_file_path({"TALO_MODELS_FILE": "/x/m.toml"}).as_posix() == "/x/m.toml"
    assert models_file_path({"XDG_CONFIG_HOME": str(tmp_path)}) == tmp_path / "talo/models.toml"


def test_missing_default_file_means_empty_config(tmp_path):
    assert load_models_config_from_env({"XDG_CONFIG_HOME": str(tmp_path)}).models == {}


def test_missing_explicit_file_is_an_error(tmp_path):
    with pytest.raises(InvalidInputError):
        load_models_config_from_env({"TALO_MODELS_FILE": str(tmp_path / "missing.toml")})


def test_invalid_toml_is_typed_error(tmp_path):
    bad = tmp_path / "models.toml"
    bad.write_text("[models.x\n")
    with pytest.raises(InvalidInputError):
        load_models_config(bad)


def test_cli_models_list(repo_root, monkeypatch, capsys):
    monkeypatch.setenv("TALO_MODELS_FILE", str(repo_root / "models.example.toml"))
    monkeypatch.setenv("TALO_DECISION_MODEL_TRIAGE", "dev-fake")
    monkeypatch.delenv("TALO_DECISION_MODEL", raising=False)
    monkeypatch.delenv("TALO_DECISION_MODEL_ROUTE", raising=False)
    monkeypatch.delenv("TALO_DECISION_MODEL_SELECT_MANY", raising=False)
    assert main(["models", "list"]) == 0
    profiles = json.loads(capsys.readouterr().out)["profiles"]
    assert profiles["route"] == {"model": "laya-en", "source": "default_config"}
    assert profiles["triage"] == {"model": "dev-fake", "source": "profile_env"}
    assert profiles["select_many"] == {"model": "haiku", "source": "profile_config"}
