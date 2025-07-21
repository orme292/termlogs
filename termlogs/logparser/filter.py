from typing import Tuple
import re
from datetime import datetime, timedelta


def parse_hour(hour_str: str) -> int:
    match = re.match(r"(\d{1,2})(AM|PM)", hour_str.upper().strip())
    if not match:
        raise ValueError(f"Invalid hour format: {hour_str}, should be like 12PM or 3AM")

    hour = int(match.group(1))
    period = match.group(2) # AM or PM

    if period == "AM" and hour == 12:
        return 0 # if 12AM, return 00 hours.
    elif period == "PM" and hour != 12:
        return hour + 12 # if PM, return hour + 12. e.g., 1PM returns as 13.

    return hour # return hour when between 1AM and 12PM.


def build_time_threshold(year: int, month: int, day: int, hour: str, range_: int) -> Tuple[datetime, datetime]:
    # hour is provided in 12-hour time with AM/PM (e.g., 1PM)
    # it needs to be converted to a 24-hour representation (e.g., 13).
    hour = parse_hour(hour)

    try:
        # start_dt (start time) is always right now
        start_ts = datetime(year, month, day, hour)
    except ValueError as e:
        raise ValueError(f"{e}")

    # end_ts (end time) is always the start time + the provided range in hours.
    end_ts = start_ts + timedelta(hours=range_)

    return start_ts, end_ts
