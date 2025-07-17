from typing import Tuple
import re
from argparse import Namespace
from datetime import datetime, timedelta


def parse_hour(hour_str: str) -> int:
    match = re.match(r"(\d{1,2})(AM|PM)", hour_str.upper())
    if not match:
        raise ValueError(f"Invalid hour format: {hour_str}")
    hour = int(match.group(1))

    if match.group(2) == "PM":
        hour += 12

    return hour

def build_time_range(args: Namespace) -> Tuple[datetime, datetime]:
    now = datetime.now()
    year = args.year if args.year else now.year
    hour = parse_hour(args.hour)

    try:
        start_dt = datetime(year, args.month, args.day, hour)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

    end_dt = start_dt + timedelta(hours=args.range)

    return start_dt, end_dt