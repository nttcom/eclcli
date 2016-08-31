__all__ = ['__version__']

import pbr.version
import os

DEFAULT_VERSION = 'v1.0'
SERVICE_TYPE = 'storage'

__version__ = DEFAULT_VERSION

# version_info = pbr.version.VersionInfo('python-storageclient')

# try:
#     __version__ = version_info.version_string()
# except AttributeError:
#     __version__ = None
