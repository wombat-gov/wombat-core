"""WOMBATpass IaC plugin system.

This package provides the framework-agnostic IaC abstraction layer:

- :class:`~wombat.iac.base.IaCBlock` — a single parsed IaC construct
- :class:`~wombat.iac.base.IaCState` — aggregated state from all parsed files
- :class:`~wombat.iac.base.IaCPlugin` — protocol every plugin must satisfy
- :data:`~wombat.iac.registry.registry` — global plugin registry

Importing this package also imports all bundled plugins so they are
registered automatically::

    from wombat.iac import registry
    plugin = registry.get("terraform")   # always available after this import
"""

from wombat.iac.base import IaCBlock, IaCPlugin, IaCState
from wombat.iac.registry import registry

# Trigger plugin self-registrations
import wombat.iac.plugins  # noqa: F401, E402

__all__ = [
    "IaCBlock",
    "IaCState",
    "IaCPlugin",
    "registry",
]
