import click
from datetime import datetime

import termlogs as t

NOW = datetime.now()

@click.group()
def cli() -> None:
    pass

@cli.command(help="Search session logs for a given time range.")
@click.option("--dir", "dir_", type=str, default="", help="Override session log directory")
@click.option("-y", "--year", type=int, default=NOW.year, help="Year (2025), defaults to current year")
@click.option("-m", "--month", type=int, default=NOW.month, help="Month (04), defaults to current month")
@click.option("-d", "--day", type=int, default=NOW.day, help="Day (01), defaults to current day")
@click.option("-t", "--hour", required=True, type=str, help="Hour string (2PM, 1AM, 12AM, etc)")
@click.option("-r", "--range", "range_", type=int, default=1, help="Number of hours to search past starting hour (1, 5, 12). Less than 72, defaults to 1")
@click.option("-l", "--screen", is_flag=True, help="Output to screen instead of temp file")
def time(dir_: str, year: int, month: int, day: int, hour: str, range_: int, screen: bool) -> None:
    try:
        log_dir = t.config.get_session_logs_directory(dir_)
    except KeyError as e:
        print(f"Could not get session logs directory: {e}")
        exit(0)

    try:
        start_dt, end_dt = t.filter.build_time_range(year, month, day, hour, range_)
    except ValueError as e:
        print(f"Invalid time value: {e}")
        exit(0)

    print(f"Searching session logs for {start_dt.strftime('%Y-%m-%d %I:%M:%S %p')} "
      f"to {end_dt.strftime('%Y-%m-%d %I:%M:%S %p')}...")

    files = t.scanner.list_matching_files(log_dir, start_dt)
    print(f"Found {len(files)} matching files.\n")

    results = {}
    for file in files:
        print(f"{file}...")
        matches = list(t.parser.parse_file(file, start_dt, end_dt))
        if matches:
            results[file] = matches

    if screen:
        t.screen.output_by_group(results)
        exit(0)

    print("Generating results file...")
    t.fo.output_to_file(results,"")

@cli.command(help="Clean up session logs.")
@click.option("--dir", "dir_", type=str, default="", help="Override session log directory")
@click.option("--max-mb", type=int, default=1000, help="The maximum size that log files in the session directory should consume.")
def clean(max_mb: int, dir_: str) -> None:
    try:
        t.clean.do(max_mb, dir_)
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        exit(0)
    except ValueError as e:
        print(f"ValueError: {e}")
        exit(0)
    except Exception as e:
        print(f"{e}")
        exit(0)

if __name__ == "__main__":
    t.screen.print_header()

    cli()