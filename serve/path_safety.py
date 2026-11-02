"""Path confinement for the internal web UI's filesystem endpoints.

``/api/scan``, ``/api/auto-fix`` and ``/api/auto-fix/rollback`` all accept a
path from the browser.  Without a guard that is an arbitrary read/write
primitive, so every path is resolved and checked against an explicit base
directory before it reaches the filesystem.  The base defaults to the
server's working directory; set ``WOMBAT_SCAN_BASE_DIR`` to the workspace
root you want to expose to the internal UI.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_ENV = "WOMBAT_SCAN_BASE_DIR"


class PathSafetyError(ValueError):
    """Raised when a caller-supplied path leaves the permitted base directory."""


def scan_base_dir() -> Path:
    """Return the resolved directory every serve path must stay inside."""
    configured = os.environ.get(BASE_ENV, "").strip()
    return Path(configured).expanduser().resolve() if configured else Path.cwd().resolve()


def resolve_scan_path(raw: str) -> Path:
    """Resolve *raw* and require the result to live inside :func:`scan_base_dir`.

    The realpath + ``startswith`` check catches ``..`` traversal, absolute
    paths outside the base and symlinks that point outside it.  The path must
    exist and be a regular file or directory.
    """
    base = scan_base_dir()
    try:
        supplied = Path(raw).expanduser()
        resolved = supplied.resolve() if supplied.is_absolute() else (base / supplied).resolve()
    except (OSError, ValueError) as exc:
        raise PathSafetyError(f"Invalid path: {raw}") from exc

    base_real = os.path.realpath(base)
    resolved_real = os.path.realpath(resolved)
    if resolved_real != base_real and not resolved_real.startswith(base_real + os.sep):
        raise PathSafetyError(
            f"Path '{raw}' is outside the allowed scan base directory ({base}). "
            f"Set {BASE_ENV} to the workspace root you want to allow."
        )
    try:
        Path(resolved_real).relative_to(base_real)
    except ValueError as exc:
        raise PathSafetyError(
            f"Path '{raw}' is outside the allowed scan base directory ({base}). "
            f"Set {BASE_ENV} to the workspace root you want to allow."
        ) from exc

    safe_path = Path(resolved_real)
    if not safe_path.exists():
        raise PathSafetyError(f"Path does not exist on the server: {safe_path}")
    if not (safe_path.is_dir() or safe_path.is_file()):
        raise PathSafetyError(f"Path is not a file or directory: {safe_path}")
    return safe_path
