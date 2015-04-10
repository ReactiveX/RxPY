from nose import SkipTest

import sys
if sys.version_info.major < 3:
    raise SkipTest("keyword `nonlocal` not available before Python 3")

from .py3_asyncioscheduler import *