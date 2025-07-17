import argparse
from datetime import datetime

from config import config
from logparser import filter, parser
from scanner import scanner
from output import file as fo, screen

NOW = datetime.now()

def parse_args() -> argparse.Namespace:
    year: int = NOW.year
    month: int = NOW.month
    day: int = NOW.day

    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="Session log directory (overrides config file)")
    ap.add_argument("--year", type=int, default=year, help="4 digit year (2025)")
    ap.add_argument("--month", type=int, default=month, help="2 digit month (04)")
    ap.add_argument("--day", type=int, default=day, help="2 digit day (01)")
    ap.add_argument("--hour", required=True, type=str, help="Hour string (2PM, 1AM, 12AM, etc)")
    ap.add_argument("--range", type=int, default=1, help="Number of hours to search beyond the starting point")
    ap.add_argument("--screen", type=bool, default=False, help="Output to screen instead of temp file")

    return ap.parse_args()

def main():
    args = parse_args()
    if args.range > 24:
        print("Range too high. Range cannot be higher than 24.")
        exit(0)

    try:
        log_dir = config.get_session_logs_directory()
    except KeyError as e:
        print(f"Key is missing from config file: {e}")
        exit(0)

    try:
        start_dt, end_dt = filter.build_time_range(args)
    except ValueError as e:
        print(f"Invalid time value: {e}")
        exit(0)

    files = scanner.list_matching_files(log_dir, start_dt)

    results = {}
    for file in files:
        matches = list(parser.parse_file(file, start_dt, end_dt))
        if matches:
            results[file] = matches

    if args.screen:
        screen.output_by_group(results)
        exit(0)

    fo.output_to_file(results,"")


if __name__ == "__main__":
    main()
