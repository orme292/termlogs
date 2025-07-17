import argparse
import humanize
import datetime
from pathlib import Path
from send2trash import send2trash
from config import config

def do(args: argparse.Namespace) -> None:
    if not args.cleanup: return

    if args.max_mb <= 0: raise ValueError("Max size cannot be 0.")

    check_and_cleanup_logs(args.max_mb)


def check_and_cleanup_logs(max_size_mb):
    log_dir = config.get_session_logs_directory()
    log_path = Path(log_dir)
    if not log_path.is_dir():
        raise Exception(f"Error: {log_dir} is not a valid directory.")

    # Gather all `.log` files with their sizes and ctimes
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

    total_size_mb = total_size / (1024 * 1024)
    print(f"Total .log files size: {humanize.naturalsize(total_size)} ({total_size_mb:.2f} MB)")

    if total_size_mb <= max_size_mb:
        raise Exception(f".log files are under {max_size_mb} MB, no cleanup needed.")

    proceed = input(f"Total size exceeds {max_size_mb} MB. Review and delete oldest files? [y/N]: ").strip().lower()
    if proceed != 'y':
        raise Exception("Cleanup cancelled.")

    # Sort files by creation time (oldest first)
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
        send2trash(str(entry['path']))
        print(f"Moved to trash: {entry['path']}")

    print("Cleanup complete.")
    exit(0)