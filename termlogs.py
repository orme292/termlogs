import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from datetime import datetime
from typing import Tuple

import termlogs as t

NOW = datetime.now()


@click.group()
def cli() -> None:
    pass


def get_session_logs_directory(dir_: str) -> str:
    try:
        log_dir = t.config.get_session_logs_directory(dir_)
    except KeyError as e:
        print(f"Could not get session logs directory: {e}")
        exit(0)
    except FileNotFoundError as e:
        print(f"Could not find session logs directory: {e}")
        exit(0)
    except Exception as e:
        print(f"Generic Error: {e}")
        exit(0)

    return log_dir


@cli.command(help="Search session logs for a given time range.")
@click.option("--dir", "dir_", type=str, default="", help="Override session log directory")
@click.option("-y", "--year", type=int, default=NOW.year, help="Year (2025), defaults to current year")
@click.option("-m", "--month", type=int, default=NOW.month, help="Month (04), defaults to current month")
@click.option("-d", "--day", type=int, default=NOW.day, help="Day (01), defaults to current day")
@click.option("-t", "--hour", required=True, type=str, help="Hour string (2PM, 1AM, 12AM, etc)")
@click.option("-r", "--range", "range_", type=int, default=1,
              help="Number of hours to search past starting hour (1, 5, 12). Less than 72, defaults to 1")
@click.option("-l", "--screen", is_flag=True, help="Output to screen instead of temp file")
def time(dir_: str, year: int, month: int, day: int, hour: str, range_: int, screen: bool) -> None:
    log_dir = get_session_logs_directory(dir_)

    try:
        start_dt, end_dt = t.filter.build_time_threshold(year, month, day, hour, range_)
    except ValueError as e:
        print(f"Invalid time value: {e}")
        exit(0)

    print(f"Searching session logs for {start_dt.strftime('%Y-%m-%d %I:%M %p')} "
          f"to {end_dt.strftime('%Y-%m-%d %I:%M %p')}...")

    files = t.scanner.find_logs_by_threshold(log_dir, start_dt, end_dt)
    print(f"Found {len(files)} matching files.\n")

    # for each file, all matching lines should be returned
    # then, to display the results, each day will have its own header
    # then each line from the log falling under that day will be displayed with ONLY the timestamp.
    # Something like:
    #
    # ===== July 24, 2025 =====
    # [5:02:01 PM] $ .......
    # [5:02:02 PM] $ .......
    #
    # ===== July 25, 2025 =====
    # etc...
    #
    # parse file should return timestamp, line (if it matches the time range)
    # and then, the output function should deal with this correctly.
    # ds = datetime.strptime(timestamp, "%m/%d/%Y")
    # ts = datetime.strptime(timestamp, "%I:%M:%S.%f %p")
    results = {Tuple[str, str]}
    for file in files:
        print(f"{file}...")
        matches = list(t.parser.parse_file(file, start_dt, end_dt))
        if matches:
            results[file] = matches

    if screen:
        t.screen.output_by_group(results)
        exit(0)

    print("Generating results file...")
    t.fo.output_to_file(results, "")


@cli.command(help="Clean up session logs.")
@click.option("--dir", "dir_", type=str, default="", help="Override session log directory")
@click.option("--max-mb", type=int, default=1000,
              help="The maximum size that log files in the session directory should consume.")
def clean(max_mb: int, dir_: str) -> None:
    log_dir = get_session_logs_directory(dir_)

    try:
        t.clean.do(max_mb, log_dir)
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        exit(0)
    except ValueError as e:
        print(f"ValueError: {e}")
        exit(0)
    except Exception as e:
        print(f"{e}")
        exit(0)


@cli.command("string")
@optgroup.group("Search options")
@optgroup.option("-s", "--string", "string_", required=True, type=str, help="String or regex to search for")
@optgroup.option("-r", "--is-regex", is_flag=True, help="Interpret string as a regex")
@optgroup.option("-i", "--ignore-case", is_flag=True, help="Ignore case when searching for string.")
@optgroup.group("Date filter options")
@optgroup.option("--start", type=str, help="Starting date. 07152025 (July 15, 2025)")
@optgroup.option("--end", type=str, help="Ending date. 07162025 (July 16, 2025)")
@optgroup.group("Output options")
@optgroup.option("-l", "--screen", is_flag=True, help="Output to screen instead of temp file")
@optgroup.group("Context options")
@optgroup.option("-a", "--ahead", type=int, default=5, help="Lines to show ahead of result.")
@optgroup.option("-b", "--behind", type=int, default=5, help="Lines to show behind result.")
@optgroup.option("--surround", type=int, default=0, help="Lines to show before and after result.")
@optgroup.group("Directory options")
@optgroup.option("--dir", "dir_", type=str, default="", help="Override session log directory")
def string(dir_: str, string_: str, start: str, end: str, is_regex: bool, ignore_case: bool, screen: bool, ahead: int,
           behind: int, surround: int) -> None:
    if (ahead or behind) and surround:
        print("Error: Cannot specify both --ahead and --behind or --surround.")
        exit(0)

    log_dir = get_session_logs_directory(dir_)

    try:
        files = t.scanner.find_logs_by_date_range(log_dir, start, end)
    except Exception as e:
        print(f"Error: {e}")
        exit(0)

    if surround:
        ahead = surround
        behind = surround

    results = t.str_match.search_logs(string_, is_regex, files, ignore_case, ahead=ahead, behind=behind, screen=screen)

    if results is None or len(results) == 0:
        print("No results found.")
        exit(0)

    if screen:
        for each in results:
            print("\n")
            for line in each:
                print(line)
            print("\n")
    exit(0)

if __name__ == "__main__":
    t.screen.print_header()

    cli()
