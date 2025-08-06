from datetime import datetime
from pathlib import Path
import os
from typing import List, Optional

BASIC_DTO_FMT = "%m%d%Y"
BASIC_DT_FMT = "%m%d%Y:%H"


def readable_datestamp(ts: datetime.timestamp) -> str:
    fmt = "%m/%d/%Y %H:%M"
    return datetime.fromtimestamp(ts).strftime(fmt)


def parse_cli_dt_input(dt: str) -> datetime.timestamp:
    try:
        return parse_date(dt, BASIC_DT_FMT)
    except ValueError:
        return parse_date(dt, BASIC_DTO_FMT)
    except Exception as e:
        print(e)
        raise ValueError(f"Date should be formatted as MMDDYYYY:HH or MMDDYYYY, got: {dt}") from e


def parse_date(string: str, fmt: Optional[str]) -> datetime:
    if not fmt: fmt = BASIC_DTO_FMT
    return datetime.strptime(string, fmt)


def find_logs(log_path: Path, start: Optional[datetime.timestamp], end: Optional[datetime.timestamp]) -> List[Path]:
    if not start and not end:
        return find_all_logs(log_path)

    if start > end:
        raise ValueError("Start time cannot be greater than end time.")

    files = []

    print(f"Searching for logs between {readable_datestamp(start)} and {readable_datestamp(end)}...\n")

    for file in os.listdir(log_path):
        if not file.endswith(".log"):
            continue

        fullpath = os.path.join(log_path, file)
        try:
            mtime = os.path.getmtime(fullpath)
            ctime = os.path.getctime(fullpath)
            include = (start <= mtime <= end) or (start <= ctime <= end)
            if include:
                files.append(Path(fullpath))
        except OSError:
            continue

    return sorted(files)


def find_all_logs(log_path: Path) -> List[Path]:
    files = []

    for file in os.listdir(log_path):
        if not file.endswith(".log"):
            continue

        try:
            fullpath = os.path.join(log_path, file)
            files.append(Path(fullpath))
        except OSError:
            continue

    return sorted(files)
