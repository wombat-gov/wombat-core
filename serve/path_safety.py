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

    Only string-level ``os.path`` operations run on the caller-supplied value
    until the containment check has passed: ``Path.expanduser()`` and
    ``Path.resolve()`` are themselves filesystem accesses, so using them here
    would touch an unvalidated path.  ``os.path.realpath`` normalises ``..``,
    absolute paths and symlinks without being treated as a path sink, and the
    ``startswith`` check is the form CodeQL recognises as a safe-access guard.
    """
    base_real = os.path.realpath(scan_base_dir())
    # ``join(base, "")`` keeps the trailing separator (and handles base == "/"
    # correctly, where naive concatenation would produce "//").
    base_prefix = os.path.join(base_real, "")
    try:
        expanded = os.path.expanduser(raw)
        candidate = os.path.realpath(
            expanded if os.path.isabs(expanded) else os.path.join(base_real, expanded)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        # RuntimeError: `~user` could not be expanded to a home directory.
        raise PathSafetyError(f"Invalid path: {raw}") from exc

    if candidate == base_real:
        safe_path = Path(base_real)
    elif candidate.startswith(base_prefix):
        safe_path = Path(candidate)
    else:
        raise PathSafetyError(
            f"Path '{raw}' is outside the allowed scan base directory ({base_real}). "
            f"Set {BASE_ENV} to the workspace root you want to allow."
        )

    if not safe_path.exists():
        raise PathSafetyError(f"Path does not exist on the server: {safe_path}")
    if not (safe_path.is_dir() or safe_path.is_file()):
        raise PathSafetyError(f"Path is not a file or directory: {safe_path}")
    return safe_path
