import os
from datetime import datetime

def list_matching_files(log_dir: str, threshold_dt: datetime) -> list:
    threshold_ts = threshold_dt.timestamp()
    files = []

    for each in os.listdir(log_dir):
        if not each.endswith(".log"):
            continue

        fpath = os.path.join(log_dir, each)
        try:
            mtime = os.path.getmtime(fpath)
            if mtime >= threshold_ts:
                files.append(fpath)
        except OSError:
            continue

    return sorted(files)