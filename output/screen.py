import re

DATETIME_RE = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2}\.\d{3} (?:AM|PM))]")
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"

def highlight_ts(line: str) -> str:
    return DATETIME_RE.sub(lambda m: f"{ANSI_CYAN}[{ANSI_YELLOW}{m.group(1)}{ANSI_CYAN}]{ANSI_RESET}   ", line)

def output_by_group(results: dict) -> None:
    for filepath, lines in results.items():
        print(f"\n=== {filepath} ===")
        for line in lines:
            print(highlight_ts(line))
        print("\n\n")
