# content of conftest.py
import sys

collect_ignore = []
if sys.version_info < (3, 5, 0):
    collect_ignore.append("test_async_scheduler.py")
