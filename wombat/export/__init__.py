"""WOMBATpass monitoring/observability export plugin system.

Import the registry and plugins via::

    from wombat.export import registry
    from wombat.export.plugins import grafana, webhook  # triggers self-registration

Or import the whole package to auto-register all bundled plugins::

    import wombat.export.plugins  # noqa: F401
"""
