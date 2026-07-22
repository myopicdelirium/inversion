"""Run provenance. Every run writes manifest.json next to its outputs:
seed, config hash, git SHA, package versions, timestamp (CLAUDE.md).
"""

import datetime
import json
import pathlib
import subprocess
import sys

import numpy as np

from .config import Config

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def build_manifest(seed: int, config: Config) -> dict:
    return {
        "seed": seed,
        "config_hash": config.config_hash(),
        "git_sha": _git_sha(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "timestamp_utc": datetime.datetime.now(datetime.UTC).isoformat(
            timespec="seconds"
        ),
    }


def write_manifest(path: pathlib.Path, seed: int, config: Config) -> None:
    path.write_text(json.dumps(build_manifest(seed, config), indent=2) + "\n")
