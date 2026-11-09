"""`talo` command line. JSON on stdout for machine callers, diagnostics on stderr."""

import argparse
import json
import sys
from collections.abc import Sequence

from talo import __version__
from talo.core.errors import NotImplementedYetError, TaloError
from talo.decisions.models import (
    PROFILE_IDS,
    load_models_config_from_env,
    models_file_path,
    select_model,
)
from talo.modules import BUILTIN_MANIFESTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="talo", description="Local decision and execution service"
    )
    parser.add_argument("--version", action="version", version=f"talo {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="execute a registered module or pipeline")
    run.add_argument("module_id")
    run.add_argument("--input", required=True, help="workspace-relative input file")
    run.add_argument("--limit", type=int, help="maximum IDs to display")

    inspect = sub.add_parser("inspect", help="fetch an evidence record or a page of results")
    inspect.add_argument("ref")
    inspect.add_argument("--id", dest="record_id")

    modules = sub.add_parser("modules", help="discover modules")
    modules_sub = modules.add_subparsers(dest="modules_command", required=True)
    modules_sub.add_parser("list", help="list registered modules")

    models = sub.add_parser("models", help="inspect configured decision models")
    models_sub = models.add_subparsers(dest="models_command", required=True)
    models_sub.add_parser("list", help="list models and which one each profile selects")

    return parser


def _emit(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _models_list() -> dict:
    config = load_models_config_from_env()
    profiles: dict[str, dict] = {}
    for profile in PROFILE_IDS:
        try:
            profiles[profile] = select_model(profile, config).model_dump(exclude={"profile"})
        except TaloError as error:
            profiles[profile] = {"error": error.code, "message": error.message}
    return {
        "models_file": str(models_file_path()),
        "models": {name: spec.model_dump(mode="json") for name, spec in config.models.items()},
        "profiles": profiles,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "modules" and args.modules_command == "list":
            _emit([m.model_dump(mode="json") for m in BUILTIN_MANIFESTS.values()])
            return 0
        if args.command == "models" and args.models_command == "list":
            _emit(_models_list())
            return 0
        raise NotImplementedYetError(f"'talo {args.command}' is not implemented yet")
    except TaloError as error:
        _emit(error.to_response().model_dump(mode="json"))
        print(f"talo: {error.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
