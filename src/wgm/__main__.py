"""Command-line entry point for a non-executing routing recommendation."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from .router import recommend_route


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 2:
        print("usage: python -m wgm TASK.json REGISTRY.json", file=sys.stderr)
        return 2
    try:
        task = json.loads(Path(arguments[0]).read_text(encoding="utf-8"))
        registry = json.loads(Path(arguments[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"input_error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(recommend_route(task, registry), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
