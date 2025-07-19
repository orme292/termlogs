import re

from ..output.format import clean_line

DATETIME_RE = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2}\.\d{3} (?:AM|PM))]")
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[92m"  # Bright green
ANSI_WHITE = "\033[97m"  # Bright white


def highlight_ts(line: str) -> str:
    return DATETIME_RE.sub(lambda m: f"{ANSI_YELLOW}[{ANSI_CYAN}{m.group(1)}{ANSI_RESET}{ANSI_YELLOW}]{ANSI_RESET} ", line)

def output_by_group(results: dict) -> None:
    for filepath, lines in results.items():
        print(f"\n=== {filepath} ===")
        for line in lines:
            cleaned = clean_line(line)
            print(highlight_ts(cleaned))
        print("\n")

def print_header() -> None:
    print(f"\n{ANSI_GREEN}Termlogs{ANSI_WHITE} - iTerm Session Log Parser{ANSI_RESET}\n")