import argparse
from datetime import datetime

from config import config
from logparser import filter, parser
from scanner import filesize, scanner
from output import file as fo, screen

NOW = datetime.now()

def parse_args() -> argparse.Namespace:
    year: int = NOW.year
    month: int = NOW.month
    day: int = NOW.day

    ap = argparse.ArgumentParser()
    span = ap.add_argument_group("Time Filters", "Options to filter logs by date, hour, and range hours.")
    span.add_argument("--dir", help="Session log directory (overrides config file)")
    span.add_argument("-y", "--year", type=int, default=year, help=f"Four-digit year (2025), defaults to {year}")
    span.add_argument("-m", "--month", type=int, default=month, help=f"Two-digit month (04), defaults to {month}")
    span.add_argument("-d", "--day", type=int, default=day, help=f"Two-digit day (01), defaults to {day}")
    span.add_argument("-t", "--hour", type=str, help="Hour string (2PM, 1AM, 12AM, etc)")
    span.add_argument("-r", "--range", type=int, default=1, help="Number of hours to search past starting hour (1, 5, 12), less than 72, defaults to 1")

    out = ap.add_argument_group("Output", "Options to control the program output")
    out.add_argument("-l", "--screen", action='store_true', help="Output to screen instead of temp file")

    file = ap.add_argument_group("Session Log Options", "Options to clean up the session logs directory.")
    file.add_argument("-x", "--cleanup", action='store_true', help="Clean up session logs")
    file.add_argument("--max-mb", type=int, default=1024, help="The maximum size that log files in the session directory should consume.")

    args = ap.parse_args()

    if not args.cleanup and not args.hour:
        ap.error("argument -t/--hour is required unless --cleanup is specified")

    return args

def main():
    screen.print_header()

    args = parse_args()
    if args.range > 72:
        print("Range too high. Range cannot be higher than 72.")
        exit(0)

    try:
        if args.cleanup: filesize.do(args)
    except ValueError as e:
        print(f"Error: {e}")
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(0)

    try:
        log_dir = config.get_session_logs_directory()
    except KeyError as e:
        print(f"Could not get session logs directory: {e}")
        exit(0)

    try:
        start_dt, end_dt = filter.build_time_range(args)
    except ValueError as e:
        print(f"Invalid time value: {e}")
        exit(0)

    print("Checking session logs...")
    files = scanner.list_matching_files(log_dir, start_dt)

    print("Scanning session logs...")
    results = {}
    for file in files:
        matches = list(parser.parse_file(file, start_dt, end_dt))
        if matches:
            results[file] = matches

    if args.screen:
        screen.output_by_group(results)
        exit(0)

    print("Generating results file...")
    fo.output_to_file(results,"")

if __name__ == "__main__":
    main()
