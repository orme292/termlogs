import os
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

BASIC_DATE_FORMAT = "%m%d%Y"


def parse_basic_date(date_str: str) -> datetime.date:
    try:
        new_date = datetime.strptime(date_str, BASIC_DATE_FORMAT).date()
    except ValueError:
        raise ValueError(f"Date should be formatted as MMDDYYYY (like 05152025), got: {date_str}")

    return new_date


def find_logs_by_threshold(log_dir: str, start_dt: datetime, end_dt: datetime) -> list:
    start_ts = start_dt.timestamp()
    end_ts = end_dt.timestamp()
    files = []

    for each in os.listdir(log_dir):
        if not each.endswith(".log"):
            continue

        fpath = os.path.join(log_dir, each)
        try:
            mtime = os.path.getmtime(fpath)
            ctime = os.path.getctime(fpath)
            include = (start_ts <= mtime <= end_ts) or (start_ts <= ctime <= end_ts)
            if include:
                files.append(fpath)
        except OSError:
            continue

    return sorted(files)


def find_logs_by_date_range(log_path: str, start_dt: Optional[str], end_dt: Optional[str]) -> List[str]:
    start_date = parse_basic_date(start_dt) if start_dt else None
    end_date = parse_basic_date(end_dt) if end_dt else None

    files = []

    log_path = Path(log_path)
    for file in log_path.iterdir():
        if not file.is_file():
            continue

        mtime = date.fromtimestamp(file.stat().st_mtime)
        ctime = date.fromtimestamp(file.stat().st_ctime)

        include = True
        if start_date and end_date:
            include = start_date <= mtime <= end_date
            if not include:
                include = start_date <= ctime <= end_date
        elif start_date:
            include = mtime >= start_date
            if not include:
                include = ctime >= start_date
        elif end_date:
            include = mtime <= end_date
            if not include:
                include = ctime <= end_date

        if include:
            files.append(str(file))

    return sorted(files)
