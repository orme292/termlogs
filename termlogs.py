import click
from click_option_group import optgroup
from datetime import datetime
from pathlib import Path
from typing import Tuple
import sys
import termlogsx as tx

NOW = datetime.now()
DEFAULT_START = datetime(1970, 1, 1)


def get_session_logs_directory(dir_: str) -> Path:
    try:
        log_dir = tx.cfg.get_session_logs_path(dir_)
    except Exception as e:
        print(f"Error: {e}")
        exit(0)

    return log_dir


@click.group()
def cli() -> None:
    pass


@cli.command(help="Search for session logs in a given time range.")
@click.option("--start", type=str, help="Starting date. 07152025:5 (July 15, 2025, 5AM)")
@click.option("--end", type=str, help="Ending date. 07162025:13 (July 16, 2025, 1PM)")
@optgroup.group("\nOutput options")
@optgroup.option("-l", "--screen", is_flag=True, help="Output to screen instead of temp file")
@optgroup.group("\nOverride options")
@optgroup.option("--dir", "dir_", type=str, default="", help="Override session log directory")
def time(dir_: str, start: str, end: str, screen: bool) -> None:
    if screen and not tx.screenout.confirm_screen(): exit(0)

    dest: Path
    log_dir = get_session_logs_directory(dir_)

    try:
        start_dt = tx.files.parse_cli_dt_input(start) if start else None
        end_dt = tx.files.parse_cli_dt_input(end) if end else None
    except Exception as e:
        print(f"Parse date: {e}")
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

    print(f"Parsing {len(files)} session logs in timeframe.")

    if not screen: dest = tx.fileout.new_temp_file()

    for file in files:
        print(f"{file}")

    for file in files:
        lines: list[str] = [f"=== {file} ==="]
        results = tx.parse.parse_file_with_time(file, start=start_ts, end=end_ts)
        for each in results:
            lines.append(f"[{each['timestamp']}]: {each['content']}")
        lines.append("\n")
        tx.fileout.save(dest, lines) if not screen else tx.screenout.output(sys.stdout, lines)

    if screen: exit(0)

    if tx.screenout.confirm_open():
        print(f"Opening {dest}...")
        tx.fileout.open_file(dest)
    else:
        print(f"Results saved to {dest}.")

    exit(0)


@cli.command(help="Clean up session logs.")
@click.option("--max-mb", type=int, default=1000,
              help="The maximum size that log files in the session directory should consume.")
@optgroup.group("\nOverride options")
@optgroup.option("--dir", "dir_", type=str, default="", help="Override session log directory")
def clean(max_mb: int, dir_: str) -> None:
    log_dir = get_session_logs_directory(dir_)

    try:
        tx.clean.start(max_mb, log_dir)
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
@click.option("-s", "--search", "search", required=True, type=str, help="String or regex to search for")
@click.option("-r", "--is-regex", is_flag=True, help="Interpret string as a regex")
@click.option("-m", "--match-case", is_flag=True, help="Search is case-sensitive.")
@optgroup.group("\nDate filter options")
@optgroup.option("--start", type=str, help="Starting date. 07152025:5 (July 15, 2025, 5AM)")
@optgroup.option("--end", type=str, help="Ending date. 07162025:13 (July 16, 2025, 1PM)")
@optgroup.group("\nOutput options")
@optgroup.option("-l", "--screen", is_flag=True, help="Output to screen instead of temp file")
@optgroup.group("\nContext options")
@optgroup.option("-a", "--ahead", type=int, default=-1, help="Lines to show ahead of result.")
@optgroup.option("-b", "--behind", type=int, default=-1, help="Lines to show behind result.")
@optgroup.option("--surround", type=int, default=-1, help="Lines to show before and after result.")
@optgroup.group("\nOverride options")
@optgroup.option("--dir", "dir_", type=str, default="", help="Override session log directory")
def grep(dir_: str, search: str, start: str, end: str, is_regex: bool, match_case: bool, screen: bool, ahead: int,
         behind: int, surround: int) -> None:
    if screen and not tx.screenout.confirm_screen(): exit(0)

    log_dir = get_session_logs_directory(dir_)

    search = search.strip().casefold() if not (match_case or is_regex) else search.strip()
    try:
        ahead, behind = get_buffer(ahead, behind, surround)
    except ValueError as e:
        print(f"CLI error: {e}")
        exit(0)

    if is_regex and match_case: print("-m/--match-case is ignored when using --is-regex/-r")

    try:
        start_dt = tx.files.parse_cli_dt_input(start) if start else None
        end_dt = tx.files.parse_cli_dt_input(end) if end else None
    except Exception as e:
        print(f"Parse date: {e}")
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

    if not screen: dest = tx.fileout.new_temp_file()

    print(f"Searching for \"{search}\" in {len(files)} files...")

    MATCHDOWN: str = "↓"
    count: int = 0
    for file in files:
        try:
            results = tx.grep.grep_search(file, search=search, start=start_ts, end=end_ts, behind=behind, ahead=ahead,
                                          regex=is_regex, match_case=match_case)
        except Exception as e:
            print(f"Grep: {e}")
            continue

        lines: list[str] = [f"=== {file} ==="]
        for group, result in results.items():
            lines.append(f" --- Match set {group} ---")
            for each in result:
                if each['match']:
                    count += 1
                    lines.append(MATCHDOWN * (len(each['timestamp']) + 4 + len(each['content'])))
                lines.append(f"[{each['timestamp']}]: {each['content']}")
            lines.append("\n")
            tx.screenout.output(sys.stdout, lines) if screen else tx.fileout.save(dest, lines)

    if count <= 0:
        print("No matches found.")
        exit(0)

    if tx.screenout.confirm_open():
        print(f"Opening {dest}...")
        tx.fileout.open_file(dest)
    else:
        print(f"Results saved to {dest}.")

    exit(0)


def get_buffer(ahead: int = -1, behind: int = -1, surround: int = -1) -> Tuple[int, int]:
    if surround > -1 and (ahead > -1 or behind > -1):
        raise ValueError("Cannot specify --ahead or --behind when using --surround.")
    elif ahead > -1 and behind > -1:
        return ahead, behind
    elif ahead > -1:
        return ahead, 0
    elif behind > -1:
        return 0, behind
    elif surround > -1:
        return 5, 5
    else:
        raise ValueError("Error getting values to create buffer.")


if __name__ == "__main__":
    tx.screenout.print_header()
    cli()
