"""Auto-import all monitoring export plugins so they self-register.

Add a new import here after creating a plugin file in this directory.
"""

from wombat.export.plugins import grafana  # noqa: F401
from wombat.export.plugins import prometheus  # noqa: F401
from wombat.export.plugins import datadog  # noqa: F401
from wombat.export.plugins import splunk  # noqa: F401
from wombat.export.plugins import slack  # noqa: F401
from wombat.export.plugins import webhook  # noqa: F401
