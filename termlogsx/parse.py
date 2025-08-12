import re
from datetime import datetime
from pathlib import Path

LOG_TIMESTAMP_REGEX = re.compile(
    r"^\[(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2}:\d{2}\.\d{3})\s*(AM|PM|am|pm)\]\s*(.*)"
)

def parse_line(line: str) -> dict:
    line = line.rstrip()  # Remove newline and any trailing spaces

    match =  LOG_TIMESTAMP_REGEX.match(line)
    if not match:
        # TEMP DEBUG:
        if line.startswith("["):
            print(f"NO MATCH >>> {line}")
        return {}

    date_part = match.group(1)
    time_part = match.group(2)
    ampm_part = match.group(3)
    content = re.sub(r"^(%\s+)", "% ", match.group(4))

    timestamp_str = f"{date_part} {time_part} {ampm_part}"
    # try:
    #     dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S.%f %p")
    # except ValueError:
    #     return {}

    return {
        "timestamp": timestamp_str,
        # "ds": dt.strftime("%m-%d-%Y"),
        # "ts": dt.strftime("%I:%M:%S.%f")[:-3],
        "content": content.strip(),
        # "dt": str(dt)
        "match": False
    }


def parse_file(file_path: Path) -> list:
    entries = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = parse_line(line)
                if parsed:
                    entries.append(parsed)

        entries.sort(key=lambda x: x["dt"])

        for entry in entries:
            entry.pop("dt", None)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return entries