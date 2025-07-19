from typing import Tuple
import re
from datetime import datetime, timedelta


def parse_hour(hour_str: str) -> int:
    match = re.match(r"(\d{1,2})(AM|PM)", hour_str.upper())
    if not match:
        raise ValueError(f"Invalid hour format: {hour_str}, it should be like 12PM or 3AM")

    hour = int(match.group(1))
    period = match.group(2)

    if period == "AM":
        if hour == 12:
            return 0
        return hour
    else:  # PM
        if hour == 12:
            return 12
        return hour + 12

def build_time_range(year: int, month: int, day: int, hour: str, range_: int) -> Tuple[datetime, datetime]:
    hour = parse_hour(hour)

    try:
        start_dt = datetime(year, month, day, hour)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

    end_dt = start_dt + timedelta(hours=range_)

    return start_dt, end_dt