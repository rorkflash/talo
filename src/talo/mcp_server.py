"""Thin MCP stdio adapter.

Milestone 1 exposes talo_run and talo_inspect, calling the core in-process.
"""

import importlib.util
import sys


def main() -> int:
    if importlib.util.find_spec("mcp") is None:
        print("talo-mcp: install the 'mcp' extra, e.g. `uv sync --extra mcp`", file=sys.stderr)
        return 1
    print("talo-mcp: the MCP adapter is not implemented yet", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
