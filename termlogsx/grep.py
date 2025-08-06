import re
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import List

LOG_TIMESTAMP_REGEX = re.compile(
    r"^\[(\d{2}/\d{2}/\d{4}),\s*(\d{1,2}:\d{2}:\d{2}\.\d{3})\s*(AM|PM|am|pm)\]\s*(.*)"
)


def parse_line(line: str) -> dict:
    line = line.rstrip()  # Remove newline and any trailing spaces

    match = LOG_TIMESTAMP_REGEX.match(line)
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
    try:
        dt = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S.%f %p")
    except ValueError:
        return {}

    return {
        "timestamp": timestamp_str,
        "ds": dt.strftime("%m::%d::%Y"),
        "ts": dt.strftime("%I::%M::%S::%f")[:-3],
        "content": content.strip(),
        "dt": dt
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


def grep_search(
        files: List[Path], search_string: str, start: datetime.timestamp, end: datetime.timestamp,
        ahead_buffer: int = 5, behind_buffer: int = 5, is_regex: bool = False, match_case: bool = False) -> dict:
    results = {}
    pattern = re.Pattern[str]

    # Compile regex if needed
    if is_regex:
        pattern = re.compile(search_string)
    elif not match_case:
        search_string = search_string.lower()

    for file in files:
        file_results = []
        match_count = 0
        buffer_behind = deque(maxlen=behind_buffer)
        ahead_queue = deque()
        post_match_mode = False

        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                line = lines[i]
                parsed = parse_line(line)
                i += 1

                if not parsed:
                    continue

                dt_ts = parsed["dt"].timestamp()
                if dt_ts < start or dt_ts > end:
                    continue

                content = parsed["content"]
                check = content if match_case else content.lower()

                is_match = (
                    pattern.search(content) if is_regex
                    else search_string in check
                )

                if post_match_mode:
                    ahead_queue.append(parsed)
                    if is_match:
                        file_results.append({
                            "match_number": match_count + 1,
                            "lines": list(ahead_queue)
                        })
                        match_count += 1
                        ahead_queue.clear()
                        post_match_mode = False
                    elif len(ahead_queue) >= ahead_buffer:
                        file_results.append({
                            "match_number": match_count,
                            "lines": list(ahead_queue)
                        })
                        ahead_queue.clear()
                        post_match_mode = False
                    continue

                if is_match:
                    parsed["matched"] = True
                    group = list(buffer_behind) + [parsed]
                    buffer_behind.clear()

                    post_match_mode = True
                    ahead_queue = deque(group)
                    match_count += 1
                else:
                    buffer_behind.append(parsed)

        except Exception as e:
            print(f"Failed to read {file}: {e}")
            continue

        if file_results:
            results[str(file)] = file_results

    return results