from nose import SkipTest

import rx
import sys
if sys.version_info.major < 3:
    raise SkipTest("async language features not available")
else:
    from .py3_tofuture import *
