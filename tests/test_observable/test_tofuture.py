from nose import SkipTest

import rx
# set also in py2, when e.g. trollius is available:
asyncio = rx.config['asyncio']
if asyncio is None:
    raise SkipTest("asyncio not available")

from .py2_3_tofuture import *
