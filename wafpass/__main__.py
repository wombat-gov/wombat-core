"""Deprecated: run ``python -m wombat`` instead."""

import warnings

warnings.warn(
    "'python -m wafpass' is deprecated after the WAF++ → Wombat rebrand; "
    "use 'python -m wombat' or the 'wombat' command instead.",
    DeprecationWarning,
    stacklevel=2,
)

from wombat.cli import app  # noqa: E402

if __name__ == "__main__":
    app()
