import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from datetime import datetime
from pathlib import Path
from typing import Tuple

import termlogs as t
import termlogsx as tx

NOW = datetime.now()
DEFAULT_START = datetime(1970, 1, 1)

@click.group()
def cli() -> None:
    pass


def get_session_logs_directory(dir_: str) -> Path:
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


@cli.command("grep", help="Search session logs for a given string or regex.")
@click.option("-s", "--string", "string_", required=True, type=str, help="String or regex to search for")
@click.option("-r", "--is-regex", is_flag=True, help="Interpret string as a regex")
@click.option("-m", "--match-case", is_flag=True, help="Search is case-sensitive.")
@optgroup.group("Date filter options")
@optgroup.option("--start", type=str, help="Starting date. 07152025:5 (July 15, 2025, 5AM)")
@optgroup.option("--end", type=str, help="Ending date. 07162025:13 (July 16, 2025, 1PM)")
@optgroup.group("Output options")
@optgroup.option("-l", "--screen", is_flag=True, help="Output to screen instead of temp file")
@optgroup.group("Context options")
@optgroup.option("-a", "--ahead", type=int, default=5, help="Lines to show ahead of result.")
@optgroup.option("-b", "--behind", type=int, default=5, help="Lines to show behind result.")
@optgroup.option("--surround", type=int, default=0, help="Lines to show before and after result.")
@optgroup.group("Directory options")
@optgroup.option("--dir", "dir_", type=str, default="", help="Override session log directory")
def grep(dir_: str, string_: str, start: str, end: str, is_regex: bool, match_case: bool, screen: bool, ahead: int,
           behind: int, surround: int) -> None:
    if (ahead or behind) and surround:
        print("Error: Cannot specify both --ahead or --behind and --surround.")
        exit(0)

    if is_regex and match_case:
        print("-m/--match-case is ignored when using --is-regex/-r")

    log_dir = tx.cfg.get_session_logs_path(dir_)

    try:
        start_dt = tx.files.parse_cli_dt_input(start) if start else None
        end_dt = tx.files.parse_cli_dt_input(end) if end else None
    except Exception as e:
        print(f"Error: {e}")
        exit(0)

    start_ts = (start_dt or DEFAULT_START).timestamp()
    end_ts = (end_dt or NOW).timestamp()

    try:
        files = tx.files.find_logs(log_dir, start=start_ts, end=end_ts)
    except ValueError as e:
        print(f"Invalid data: {e}")
        exit(0)
    except Exception as e:
        print(f"Generic Error: {e}")
        exit(0)

    if len(files) == 0:
        print("No logs found in timeframe.")
        exit(0)

    print(f"Found {len(files)} matching files.\n")

    results = tx.grep.grep_search(files, string_, start=start_ts, end=end_ts,
                        ahead_buffer=ahead, behind_buffer=behind, is_regex=is_regex, match_case=match_case)

    for file_path, matches in results.items():
        print(f"\n=== {file_path} ===")
        for match in matches:
            print(f"--- Match {match['match_number']} ---")
            for line in match["lines"]:
                ts = line["timestamp"]
                content = line["content"]
                marker = ">>> MATCH <<<" if line.get("matched") else ""
                print(f"[{ts}] {marker} {content}")


if __name__ == "__main__":
    t.screen.print_header()

    cli()
