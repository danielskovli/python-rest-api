import datetime
from .version import version_info, __version__


# Uptime things
__started_at__ = datetime.datetime.now()
uptime = lambda: datetime.datetime.now() - __started_at__