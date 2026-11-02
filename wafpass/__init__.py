"""Deprecated compatibility package — import :mod:`wombat` instead.

``wafpass`` was the package name before the WAF++ → Wombat rebrand.  It is
kept as a thin alias so existing integrations keep working for one migration
window; every import emits a :class:`DeprecationWarning`.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
import warnings

warnings.warn(
    "The 'wafpass' package is deprecated after the WAF++ → Wombat rebrand; "
    "import 'wombat' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from wombat import (  # noqa: E402,F401
    IaCBlock,
    IaCPlugin,
    IaCState,
    FindingSchema,
    LocalAttestationSchema,
    Report,
    ServerValidationSchema,
    ValidationEnvelopeSchema,
    WombatResultSchema,
    __name_full__,
    __version__,
    run_scan,
)

# Deprecated WAFpass-era name.
WafpassResultSchema = WombatResultSchema


class _WombatAliasLoader(importlib.abc.Loader):
    """Load ``wafpass.<name>`` by copying the ``wombat.<name>`` module."""

    def create_module(self, spec):  # noqa: ANN001 - importlib protocol
        return None

    def exec_module(self, module) -> None:  # noqa: ANN001 - importlib protocol
        target_name = "wombat" + module.__name__[len("wafpass"):]
        target = importlib.import_module(target_name)
        module.__dict__.update(target.__dict__)
        module.__doc__ = target.__doc__


class _WombatAliasFinder(importlib.abc.MetaPathFinder):
    """Redirect every ``wafpass.*`` submodule import to ``wombat.*``."""

    def find_spec(self, fullname, path=None, target=None):  # noqa: ANN001
        if fullname.startswith("wafpass."):
            return importlib.util.spec_from_loader(fullname, _WombatAliasLoader())
        return None


sys.meta_path.insert(0, _WombatAliasFinder())
