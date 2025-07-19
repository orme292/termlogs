import re
from datetime import datetime
from typing import Iterator, Tuple, Optional

LOG_TIMESTAMP_REGEX = re.compile(
    r"^\[(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2}:\d{2}\.\d{3})\s*(AM|PM|am|pm)\]\s*(.*)"
)

def parse_line(line: str) -> Tuple[Optional[datetime], str]:
    match = LOG_TIMESTAMP_REGEX.match(line)
    if not match:
        return None, ""

    # Fix: Include AM/PM part explicitly
    timestamp = f"{match.group(1)} {match.group(2)} {match.group(3)}"

    try:
        dt = datetime.strptime(timestamp, "%m/%d/%Y %I:%M:%S.%f %p")
    except ValueError:
        return None, ""

    return dt, line.rstrip()


def parse_file(filepath: str, start_dt: datetime, end_dt: datetime) -> Iterator[str]:
    with open(filepath, "r") as f:
        for line in f:
            dt, full_line = parse_line(line)
            if dt is not None and start_dt <= dt < end_dt:
                yield full_line
