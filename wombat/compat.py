"""Deprecated-name compatibility for the WAFpass → WOMBATpass migration.

The rebrand renamed the product from WAFpass to WOMBATpass and the CLI command
from ``wafpass`` to ``wombat``.  These helpers keep existing installations,
CI pipelines and scripts working while emitting deprecation warnings:

* ``WAFPASS_*`` environment variables are promoted to ``WOMBAT_*``.
* ``~/.wafpass`` is still used when it exists and ``~/.wombat`` does not.
* legacy ``.wafpass-*`` config/state files are still discovered.

Everything here is scheduled for removal after the migration window.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path

ENV_PREFIX = "WOMBAT_"
LEGACY_ENV_PREFIX = "WAFPASS_"

HOME_DIRNAME = ".wombat"
LEGACY_HOME_DIRNAME = ".wafpass"

DEFAULT_STATE_DIR = Path(".wombat-state")
LEGACY_STATE_DIR = Path(".wafpass-state")

DEFAULT_SERVER_CONTROLS_DIR = Path(".wombat-server-controls")
LEGACY_SERVER_CONTROLS_DIR = Path(".wafpass-server-controls")

LEGACY_SKIP_FILE = ".wafpass-skip.yml"
LEGACY_EXPORT_CONFIG = Path(".wafpass-export.yml")

_promoted = False


def warn_legacy(what: str, *, replacement: str | None = None) -> None:
    """Emit a consistent deprecation warning for an old WAFpass name."""
    suffix = f" Use {replacement} instead." if replacement else ""
    warnings.warn(
        f"{what} is deprecated after the WAF++ → Wombat rebrand.{suffix}",
        FutureWarning,
        stacklevel=3,
    )


def promote_legacy_env() -> None:
    """Copy any legacy ``WAFPASS_*`` env vars to their ``WOMBAT_*`` names.

    New names always win when both are set.  Called once on package import so
    Typer options and direct ``os.environ`` reads see the same values.
    """
    global _promoted
    if _promoted:
        return
    _promoted = True

    for key in list(os.environ):
        if not key.startswith(LEGACY_ENV_PREFIX):
            continue
        new_key = ENV_PREFIX + key[len(LEGACY_ENV_PREFIX):]
        if new_key in os.environ:
            continue
        os.environ[new_key] = os.environ[key]
        warn_legacy(f"Environment variable {key}", replacement=new_key)


def home_dir() -> Path:
    """Return ``~/.wombat``, falling back to an existing ``~/.wafpass``."""
    new = Path.home() / HOME_DIRNAME
    old = Path.home() / LEGACY_HOME_DIRNAME
    if not new.exists() and old.exists():
        warn_legacy(f"The {old} directory", replacement=str(new))
        return old
    return new


def default_state_dir() -> Path:
    """Return ``.wombat-state``, or an existing legacy ``.wafpass-state``."""
    if not DEFAULT_STATE_DIR.exists() and LEGACY_STATE_DIR.exists():
        warn_legacy(str(LEGACY_STATE_DIR), replacement=str(DEFAULT_STATE_DIR))
        return LEGACY_STATE_DIR
    return DEFAULT_STATE_DIR


def default_server_controls_dir() -> Path:
    """Return ``.wombat-server-controls`` with legacy fallback."""
    if not DEFAULT_SERVER_CONTROLS_DIR.exists() and LEGACY_SERVER_CONTROLS_DIR.exists():
        warn_legacy(str(LEGACY_SERVER_CONTROLS_DIR), replacement=str(DEFAULT_SERVER_CONTROLS_DIR))
        return LEGACY_SERVER_CONTROLS_DIR
    return DEFAULT_SERVER_CONTROLS_DIR
