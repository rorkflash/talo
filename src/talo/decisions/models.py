"""Named decision models and how each profile picks one.

Models are defined once in a TOML file. Environment variables only choose among the defined
names; they never define a model or bypass workspace policy.

Precedence, first match wins:
  1. explicit override (a `--model` flag on the request)
  2. TALO_DECISION_MODEL_<PROFILE>, e.g. TALO_DECISION_MODEL_SELECT_MANY
  3. TALO_DECISION_MODEL
  4. [profiles].<profile> in the models file
  5. [profiles].default in the models file

The environment is read by the process that builds the backend: the CLI when running
in-process, and `talo serve` once the daemon exists. Clients of the daemon switch models
per request with the override, not with their own environment.
"""

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)

from talo.core.errors import BackendUnavailableError, InvalidInputError, UnknownModelError
from talo.decisions.backends.api import ApiBackend
from talo.decisions.backends.base import DecisionBackend
from talo.decisions.backends.fake import FakeBackend
from talo.decisions.backends.local import LocalBackend
from talo.decisions.policy import BackendPolicy, check_backend_allowed

PROFILE_IDS = ("route", "triage", "select_many")
ENV_MODEL = "TALO_DECISION_MODEL"
ENV_MODELS_FILE = "TALO_MODELS_FILE"

ModelName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_-]*$")]
SelectionSource = Literal[
    "override", "profile_env", "default_env", "profile_config", "default_config"
]


class LocalModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: Literal["local"]
    adapter: Literal["laya", "mlx", "llama_cpp", "ollama"]
    checkpoint: str
    # Pinned so normal operation can run offline and runs stay reproducible.
    revision: str


class ApiModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: Literal["api"]
    provider: Literal["anthropic"]
    model: str
    effort: Literal["low", "medium", "high", "xhigh", "max"] = "low"


class FakeModelSpec(BaseModel):
    """Scripted answers by candidate ID, for development without a model."""

    model_config = ConfigDict(extra="forbid")

    backend: Literal["fake"]
    answers: dict[str, str] = Field(default_factory=dict)


ModelSpec = Annotated[LocalModelSpec | ApiModelSpec | FakeModelSpec, Field(discriminator="backend")]


class ProfileModels(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default: ModelName | None = None
    route: ModelName | None = None
    triage: ModelName | None = None
    select_many: ModelName | None = None


class ModelsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    models: dict[ModelName, ModelSpec] = Field(default_factory=dict)
    profiles: ProfileModels = Field(default_factory=ProfileModels)

    @model_validator(mode="after")
    def _profiles_reference_defined_models(self) -> "ModelsConfig":
        for profile, name in self.profiles.model_dump().items():
            if name is not None and name not in self.models:
                raise ValueError(f"[profiles].{profile} names undefined model {name!r}")
        return self


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: str
    model: str
    source: SelectionSource


def profile_env_var(profile: str) -> str:
    return f"{ENV_MODEL}_{profile.upper()}"


def models_file_path(env: Mapping[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    if explicit := env.get(ENV_MODELS_FILE):
        return Path(explicit).expanduser()
    base = env.get("XDG_CONFIG_HOME") or "~/.config"
    return Path(base).expanduser() / "talo" / "models.toml"


def load_models_config(path: Path, *, required: bool = False) -> ModelsConfig:
    """Load the models file. A missing default file means no models are configured."""
    if not path.is_file():
        if required:
            raise InvalidInputError(f"models file not found: {path}")
        return ModelsConfig()
    try:
        return ModelsConfig.model_validate(tomllib.loads(path.read_text()))
    except (tomllib.TOMLDecodeError, ValidationError) as error:
        raise InvalidInputError(f"invalid models file {path}: {error}") from error


def load_models_config_from_env(env: Mapping[str, str] | None = None) -> ModelsConfig:
    env = os.environ if env is None else env
    return load_models_config(models_file_path(env), required=bool(env.get(ENV_MODELS_FILE)))


def select_model(
    profile: str,
    config: ModelsConfig,
    *,
    env: Mapping[str, str] | None = None,
    override: str | None = None,
) -> Selection:
    if profile not in PROFILE_IDS:
        raise InvalidInputError(f"unknown decision profile {profile!r}")
    env = os.environ if env is None else env
    candidates: list[tuple[SelectionSource, str, str | None]] = [
        ("override", "the --model override", override),
        ("profile_env", profile_env_var(profile), env.get(profile_env_var(profile))),
        ("default_env", ENV_MODEL, env.get(ENV_MODEL)),
        ("profile_config", f"[profiles].{profile}", getattr(config.profiles, profile)),
        ("default_config", "[profiles].default", config.profiles.default),
    ]
    for source, origin, name in candidates:
        name = (name or "").strip()
        if not name:
            continue
        if name not in config.models:
            raise UnknownModelError(
                f"{origin} selects model {name!r}, which the models file does not define"
            )
        return Selection(profile=profile, model=name, source=source)
    raise BackendUnavailableError(
        f"no decision model configured for profile {profile!r}; "
        f"set {ENV_MODEL} or [profiles] in the models file"
    )


def build_backend(spec: LocalModelSpec | ApiModelSpec | FakeModelSpec) -> DecisionBackend:
    """Construct a backend without loading any model."""
    match spec:
        case LocalModelSpec():
            return LocalBackend(spec.adapter, spec.checkpoint, spec.revision)
        case ApiModelSpec():
            return ApiBackend(spec.provider, spec.model, effort=spec.effort)
        case FakeModelSpec():
            return FakeBackend(spec.answers)
    raise AssertionError(f"unhandled model spec: {spec!r}")


def backend_for_profile(
    profile: str,
    config: ModelsConfig,
    policy: BackendPolicy,
    *,
    env: Mapping[str, str] | None = None,
    override: str | None = None,
) -> tuple[Selection, DecisionBackend]:
    """Select, build and policy-check the backend a profile should use."""
    selection = select_model(profile, config, env=env, override=override)
    backend = build_backend(config.models[selection.model])
    check_backend_allowed(backend, policy)
    return selection, backend
