from nose import SkipTest
try:
    import asyncio
except ImportError:
    raise SkipTest("asyncio not available")

from .py3_tofuture import *