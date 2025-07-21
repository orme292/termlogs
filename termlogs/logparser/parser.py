import re
from datetime import datetime
from typing import Iterator, Tuple, Optional

LOG_TIMESTAMP_REGEX = re.compile(
    r"^\[(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2}:\d{2}\.\d{3})\s*(AM|PM|am|pm)\]\s*(.*)"
)

def parse_file(filepath: str, start_dt: datetime, end_dt: datetime) -> Iterator[Tuple[str, str]]:
    try:
        with open(filepath, "r") as f:
            for line in f:
                ts, dt, full_line = parse_line(line)
                if dt is not None and start_dt <= dt < end_dt and ts is not None:
                    yield ts, full_line
    except Exception as e:
        print(f"Error: {e}")

# Returns
def parse_line(line: str) -> Tuple[Optional[str], Optional[datetime], Optional[str]]:
    match = LOG_TIMESTAMP_REGEX.match(line)
    if not match:
        return None, None, None

    # Fix: Include AM/PM part explicitly
    timestamp = f"{match.group(1)} {match.group(2)} {match.group(3)}"

    try:
        dt = datetime.strptime(timestamp, "%m/%d/%Y %I:%M:%S.%f %p")
        ds = datetime.strptime(timestamp, "%m/%d/%Y")
        ts = datetime.strptime(timestamp, "%I:%M:%S.%f %p")
    except ValueError:
        return None, None, None

    return timestamp, dt, line.rstrip()



