from nose import SkipTest

import sys

if sys.version_info.major < 3:
    from .py2_asyncioscheduler import *
else:
    from .py3_asyncioscheduler import *