from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
