import platform

import httpx

__version__ = "0.3.1"
__url__ = "https://github.com/sco1/wheely-bucket"

USER_AGENT = (
    f"wheely-bucket/{__version__} ({__url__}) "
    f"httpx/{httpx.__version__} "
    f"{platform.python_implementation()}/{platform.python_version()}"
)
