"""
Datetime utilities for Python version compatibility.
Provides consistent datetime handling across Python 3.10-3.12.
"""

import sys
from datetime import datetime, timezone

# Python version compatibility for UTC
if sys.version_info >= (3, 11):
    try:
        from datetime import UTC
    except ImportError:
        UTC = UTC
else:
    UTC = timezone.utc


def utcnow() -> datetime:
    """
    Get current UTC datetime.

    Compatible replacement for datetime.utcnow() which is deprecated in Python 3.12.

    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(UTC)


def utc_timestamp() -> datetime:
    """
    Get current UTC timestamp.

    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(UTC)
