from datetime import timedelta

def parse_interval(interval: str) -> timedelta:
    """
    Parse the interval string into a timedelta object.
    
    :param interval: Interval string (e.g., "5m", "1h").
    :return: A timedelta object representing the interval.
    """
    if interval.endswith("m"):
        return timedelta(minutes=int(interval[:-1]))
    elif interval.endswith("h"):
        return timedelta(hours=int(interval[:-1]))
    elif interval.endswith("d"):
        return timedelta(days=int(interval[:-1]))
    else:
        raise ValueError(f"Unsupported interval format: {interval}")