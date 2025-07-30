from datetime import date, datetime
from pathlib import Path
import os
from typing import List, Optional

BASIC_DATE_FMT = "%m%d%Y"

def parse_date(fmt: str, string: str) -> datetime.date:
    return datetime.strptime(string, fmt).date()

def find_logs(log_path: Path, start: datetime, end: datetime) -> List[str]:
    start_ts = start.timestamp()
    end_ts = end.timestamp()
    files = []

    for file in os.listdir(log_path):
        if not file.endswith(".log"):
            continue

        fullpath = os.path.join(log_path, file)
        try:
            mtime = os.path.getmtime(fullpath)
            ctime = os.path.getctime(fullpath)
            include = (start_ts <= mtime <= end_ts) or (start_ts <= ctime <= end_ts)
            if include:
                files.append(fullpath)
        except OSError:
            continue

    return sorted(files)

def find_all_logs(log_path: Path) -> List[str]:
    files = []

    for file in os.listdir(log_path):
        if not file.endswith(".log"):
            continue

        try:
            fullpath = os.path.join(log_path, file)
            files.append(fullpath)
        except OSError:
            continue

    return sorted(files)

def find_logs_by_range(log_path: Path, start_dt: datetime, end_dt: Optional[datetime]) -> List[str]:
    if end_dt is None:
        end_dt = datetime.now()

    if start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    return find_logs(log_path, start_dt, end_dt)