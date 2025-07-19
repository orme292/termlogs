import humanize
import datetime
from pathlib import Path
from send2trash import send2trash
from ..config import config
from typing import Tuple

def do(max_mb: int, dir_: str="") -> None:
    if max_mb <= 0: raise ValueError("Max size cannot be 0.")
    log_path = get_session_log_path(dir_)
    cleanup_logs(max_mb, log_path)

def get_session_log_path(dir_: str="") -> Path:
    log_dir = config.get_session_logs_directory(dir_)
    log_path = Path(log_dir)
    if not log_path.exists():
        raise FileNotFoundError(f"Log dir does not exist: {log_dir}")
    if not log_path.is_dir():
        raise Exception(f"Error: {log_dir} is not a valid directory.")
    return log_path

def gather_session_log_files(log_path: Path) -> Tuple[list, int]:
    files = []
    total_size = 0
    for f in log_path.iterdir():
        if f.is_file() and f.suffix == '.log':
            stat = f.stat()
            size = stat.st_size
            ctime = stat.st_ctime
            total_size += size
            files.append({
                'path': f,
                'size': size,
                'ctime': ctime
            })

    return files, total_size


def check_dir_size(log_path: Path) -> float:
    _, total_size_bytes = gather_session_log_files(log_path)
    return total_size_bytes


def cleanup_logs(max_size_mb: int, log_path: Path) -> None:
    total_size_bytes = check_dir_size(log_path)
    total_size_mb = total_size_bytes / (1024 * 1024)
    print(f"Total session log files size: {humanize.naturalsize(total_size_bytes)} ({total_size_mb:.2f} MB)")

    if total_size_mb <= max_size_mb:
        raise Exception(f"Session log files are under {max_size_mb} MB, no cleanup needed.")

    proceed = input(f"Total size exceeds {max_size_mb} MB. Review and delete oldest files? [y/N]: ").strip().lower()
    if proceed != 'y':
        raise Exception("Cleanup cancelled.")

    # Sort files by creation time (oldest first)
    files, _ = gather_session_log_files(log_path)
    files.sort(key=lambda x: x['ctime'])

    # Determine which files to delete until we meet the target
    running_size = total_size_mb
    files_to_delete = []
    for entry in files:
        if running_size <= max_size_mb:
            break
        running_size -= entry['size'] / (1024 * 1024)
        files_to_delete.append(entry)

    if not files_to_delete:
        raise Exception("No files to delete.")

    print("\nThe following .log files will be deleted:")
    for entry in files_to_delete:
        created = datetime.datetime.fromtimestamp(entry['ctime']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {entry['path']}  (created: {created}, size: {humanize.naturalsize(entry['size'])})")

    confirm = input("\nProceed with deleting these files? [y/N]: ").strip().lower()
    if confirm != 'y':
        raise Exception("Cleanup cancelled.")

    for entry in files_to_delete:
        try:
            send2trash(str(entry['path']))
        except Exception as e:
            print(f"Error moving to trash: {entry['path']} - {e}")
            continue

        print(f"Moved to trash: {entry['path']}")

    print("Cleanup complete.")
    exit(0)