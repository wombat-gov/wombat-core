"""WOMBATpass core library — public API.

Quick start
-----------
::

    from wombat import run_scan, WombatResultSchema

    result: WombatResultSchema = run_scan(
        paths=["infra/"],
        controls_dir="controls/",
    )
    print(result.score)

Public symbols
--------------
* :func:`run_scan`             — run a compliance scan, return a result schema object
* :class:`WombatResultSchema` — Pydantic model for the wombat-result.json contract
* :class:`FindingSchema`       — Pydantic model for a single finding within a result
* :class:`Report`              — internal dataclass report (pre-schema, for CLI/PDF use)
* ``IaCPlugin``, ``IaCBlock``, ``IaCState`` — protocol types for IaC adapters
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version

from wombat.compat import promote_legacy_env as _promote_legacy_env

# Keep WAFPASS_* environment variables working during the rebrand migration.
_promote_legacy_env()

try:
    __version__ = _pkg_version("wombat-core")
except PackageNotFoundError:
    try:
        # Deprecated: the package was published as wafpass-core before the rebrand.
        __version__ = _pkg_version("wafpass-core")
    except PackageNotFoundError:
        __version__ = "1.1.2"

__name_full__ = "WOMBATpass"

# ── Result schema (public contract) ───────────────────────────────────────────
from wombat.schema import (  # noqa: E402
    FindingSchema,
    LocalAttestationSchema,
    ServerValidationSchema,
    ValidationEnvelopeSchema,
    WombatResultSchema,
)

# ── Internal report model (used by CLI, PDF reporter, etc.) ───────────────────
from wombat.models import Report  # noqa: E402

# ── IaC adapter protocol types ────────────────────────────────────────────────
from wombat.iac.base import IaCBlock, IaCPlugin, IaCState  # noqa: E402


from pathlib import Path
from typing import List, Optional


def run_scan(
    paths: List[str],
    controls_dir: str = "controls/",
    *,
    severity_filter: Optional[str] = None,
    waivers_file: Optional[str] = None,
) -> "WombatResultSchema":
    """Run a WOMBATpass compliance scan and return a structured result.

    This is the convenience public API wrapper around
    :func:`wombat.runner.run_scan`. For full control (project, branch, secret
    scanning, source snapshots, etc.) use :class:`wombat.runner.ScanConfig`
    directly.
    """
    from wombat.runner import ScanConfig, run_scan as _run_scan

    _, schema = _run_scan(ScanConfig(
        paths=[Path(p) for p in paths],
        controls_dir=Path(controls_dir),
        severity=severity_filter,
        waivers_file=Path(waivers_file) if waivers_file else None,
    ))
    return schema


__all__ = [
    "__version__",
    "__name_full__",
    "run_scan",
    "WombatResultSchema",
    "FindingSchema",
    "LocalAttestationSchema",
    "ServerValidationSchema",
    "ValidationEnvelopeSchema",
    "Report",
    "IaCPlugin",
    "IaCBlock",
    "IaCState",
]


def __getattr__(name: str):
    """Deprecated WAFpass-era public names kept as aliases."""
    if name == "WafpassResultSchema":
        from wombat.compat import warn_legacy

        warn_legacy("wombat.WafpassResultSchema", replacement="wombat.WombatResultSchema")
        return WombatResultSchema
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
