from datetime import UTC, datetime


def is_datetime_min(dt: datetime):
    diff = dt - datetime.min.replace(tzinfo=UTC)
    return abs(diff.total_seconds()) < 1e-6
