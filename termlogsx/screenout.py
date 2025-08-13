ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[92m"  # Bright green
ANSI_WHITE = "\033[97m"  # Bright white

def output(screen_buffer, data: list[str]):
    for line in data:
        # Ensure the line ends with a newline
        if not line.endswith("\n"):
            line += "\n"
        screen_buffer.write(line)
    screen_buffer.flush()

def print_header() -> None:
    print(f"\n{ANSI_GREEN}Termlogs{ANSI_WHITE} - iTerm Session Log Parser{ANSI_RESET}\n")