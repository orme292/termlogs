import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# LOG_TIMESTAMP_REGEX = re.compile(
#     r"^\[(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2}:\d{2}\.\d{3})\s*(AM|PM|am|pm)\]\s*(.*)"
# )
LOG_TIMESTAMP_REGEX = re.compile(
    r"""
    ^\[
      (?P<date>\d{2}/\d{2}/\d{4})
      (?:,\s+|\s+)                # allow either ", " or just spaces after the date
      (?P<time>\d{1,2}:\d{2}:\d{2}(?:\.\d{1,6})?)  # HH:MM:SS(.sss…)? up to microseconds
      \s*(?P<ampm>AM|PM)          # AM/PM (case-insensitive via flag)
    \]\s*
      (?P<content>.*)             # EVERYTHING after the first timestamp
    $""",
    re.VERBOSE | re.IGNORECASE,
)


def parse_line(line: str) -> dict:
    line = line.rstrip()
    m = LOG_TIMESTAMP_REGEX.match(line)
    if not m:
        return {}

    content = re.sub(r"^%\s+", "% ", m.group("content")).strip()
    timestamp_str = f"{m.group('date')} {m.group('time')} {m.group('ampm').upper()}"

    try:
        dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S.%f %p")
    except ValueError:
        dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")

    return {
        "timestamp": timestamp_str,
        "content": content,
        "dt": dt,  # datetime object
        "match": False,
    }


def parse_line_with_time(line: str, start: datetime.timestamp, end: datetime.timestamp) -> dict:
    try:
        parsed = parse_line(line)
        if not parsed:
            return {}
    except Exception as e:
        print(f"Error parsing line: {e}")
        return {}

    dt = parsed["dt"]
    dt_ts = dt.timestamp()

    if dt_ts < start or dt_ts > end:
        print(f"Line out of time range: {dt_ts} < {start} or {dt_ts} > {end}")
        return {}

    return parsed


def parse_file(file_path: Path) -> list:
    entries: List[Dict[str, Any]] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = parse_line(line)
                if parsed:
                    entries.append(parsed)

        entries.sort(key=lambda x: x["dt"])
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return entries


def parse_file_with_time(file_path: Path, start: datetime.timestamp, end: datetime.timestamp) -> list:
    entries: List[Dict[str, Any]] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = parse_line_with_time(line, start, end)
                if parsed:
                    entries.append(parsed)

            entries.sort(key=lambda x: x["dt"])
    except OSError as e:
        print(f"File error: {file_path}: {e}")
    except Exception as e:
        print(f"Error reading with time: {file_path}: {e}")
    return entries
