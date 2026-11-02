"""Backward-compatibility shim — Terraform parser public API.

Code that previously imported from ``wombat.parser`` continues to work
unchanged.  New code should import directly from ``wombat.iac``.

    # old (still works)
    from wombat.parser import TerraformBlock, TerraformState, parse_terraform

    # new (preferred)
    from wombat.iac import IaCBlock, IaCState, registry
"""

from __future__ import annotations

from pathlib import Path

# Re-export generic types under the old Terraform-specific names.
from wombat.iac.base import IaCBlock as TerraformBlock  # noqa: F401
from wombat.iac.base import IaCState as TerraformState  # noqa: F401

# Ensure the terraform plugin (and all others) are registered.
import wombat.iac  # noqa: F401


def parse_terraform(path: Path) -> TerraformState:
    """Parse all ``.tf`` files under *path* and return a :class:`TerraformState`.

    This is a convenience wrapper around the Terraform plugin; equivalent to::

        from wombat.iac import registry
        registry.get("terraform").parse(path)

    Args:
        path: Directory containing ``.tf`` files, or a single ``.tf`` file.

    Returns:
        :class:`TerraformState` (alias for :class:`~wombat.iac.base.IaCState`)
        with all parsed blocks.
    """
    from wombat.iac.registry import registry
    plugin = registry.get("terraform")
    if plugin is None:  # should never happen after importing wombat.iac
        raise RuntimeError("Terraform plugin is not registered.")
    return plugin.parse(path)


__all__ = ["TerraformBlock", "TerraformState", "parse_terraform"]
