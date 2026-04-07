import platform

import niquests

__version__ = "1.0.1"
__url__ = "https://github.com/sco1/wheely-bucket"

USER_AGENT = (
    f"wheely-bucket/{__version__} ({__url__}) "
    f"niquests/{niquests.__version__} "
    f"{platform.python_implementation()}/{platform.python_version()}"
)
