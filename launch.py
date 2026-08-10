#!/usr/bin/env python3
"""Cross-platform launcher for the PULSE Classic Notebook application."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
NOTEBOOK_PATH = PROJECT_DIR / "PULSE.ipynb"
REQUIRED_MODULES = {
    "IPython": "ipython",
    "dotenv": "python-dotenv",
    "ipywidgets": "ipywidgets",
    "nest_asyncio": "nest-asyncio",
    "notebook": "notebook==6.5.7",
    "openpyxl": "openpyxl",
    "pandas": "pandas",
    "powerbiclient": "powerbiclient",
    "requests": "requests",
}


def environment_errors() -> list[str]:
    errors = []
    if not NOTEBOOK_PATH.is_file():
        errors.append(f"Notebook not found: {NOTEBOOK_PATH}")

    missing = [package for module, package in REQUIRED_MODULES.items() if importlib.util.find_spec(module) is None]
    if missing:
        errors.append("Missing dependencies: " + ", ".join(sorted(missing)))

    try:
        notebook_major = int(version("notebook").split(".", 1)[0])
        if notebook_major >= 7:
            errors.append(
                "PULSE requires Classic Notebook 6.x; Notebook 7 uses an incompatible frontend API."
            )
    except (PackageNotFoundError, ValueError):
        pass

    if sys.version_info < (3, 10):
        errors.append("PULSE requires Python 3.10 or newer.")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch PULSE in Jupyter Classic Notebook.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="check the local environment without starting Jupyter",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="start Jupyter without opening a browser automatically",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = environment_errors()
    if errors:
        print("PULSE cannot start:\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            f"\nInstall the project dependencies with:\n  {sys.executable} -m pip install -r "
            f'"{PROJECT_DIR / "requirements.txt"}"',
            file=sys.stderr,
        )
        return 1

    print(f"PULSE environment check passed (Classic Notebook {version('notebook')}).")
    if args.check:
        return 0

    command = [sys.executable, "-m", "notebook", NOTEBOOK_PATH.name]
    if args.no_browser:
        command.append("--no-browser")
    print(f"Launching PULSE from {PROJECT_DIR}")
    try:
        return subprocess.run(command, cwd=PROJECT_DIR, check=False).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
