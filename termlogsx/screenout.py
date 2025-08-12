def output(screen_buffer, data: list[str]):
    for line in data:
        # Ensure the line ends with a newline
        if not line.endswith("\n"):
            line += "\n"
        screen_buffer.write(line)
    screen_buffer.flush()
