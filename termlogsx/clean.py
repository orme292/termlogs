import humanize
import datetime
from pathlib import Path
from send2trash import send2trash

from typing import Tuple


def start(max_mb: int, dir_: Path) -> None:
    if max_mb <= 0: raise ValueError("Max size cannot be 0.")
    cleanup(max_mb, dir_)


def get_all_session_log_files(log_path: Path) -> Tuple[list, int]:
    files = []
    total_size: int = 0

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


def cleanup(max_size_mb: int, log_path: Path) -> None:
    files, total_size = get_all_session_log_files(log_path)
    total_size_mb = total_size / (1024 * 1024)
    print(f"There are {len(files)} session logs with a total size of {humanize.naturalsize(total_size)} ({total_size_mb:.2f} MB).")

    if total_size_mb <= max_size_mb:
        raise Exception(f"No cleanup needed, Total size is less than {max_size_mb} MB.")

    files.sort(key=lambda x: x['ctime'])

    running_size = total_size
    files_to_delete = []
    for file in files:
        if running_size <= (max_size_mb * 1024 * 1024):
            break
        running_size -= file['size']
        files_to_delete.append(file)

    if not files_to_delete:
        raise Exception("No files to delete.")

    print("\nThe following .log files will be deleted:")
    for file in files_to_delete:
        created = datetime.datetime.fromtimestamp(file['ctime']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {file['path']}  (created: {created}, size: {humanize.naturalsize(file['size'])})")

    print(f"\n{humanize.naturalsize(total_size - running_size)} will be freed. ")
    print(f"After cleanup, the total size will be {humanize.naturalsize(running_size)}.")

    confirm = input("\nAre you sure you want to delete these files? [y/n]: ").strip().lower()
    if confirm != 'y':
        raise Exception("Cleanup cancelled.")

    for entry in files_to_delete:
        try:
            send2trash(str(entry['path']))
        except Exception as e:
            print(f"Error moving file to trash: {entry['path']} - {e}")
            continue

        print(f"Moved to trash: {entry['path']}")

    print("Cleanup finished.")
    exit(0)
