import os
import subprocess
import tempfile
from pathlib import Path


def new_temp_file() -> Path:
    try:
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
    except Exception as e:
        print(f"Error creating temp file: {e}")
        exit(1)

    return Path(file.name)


def save(file: Path, data: list):
    try:
        with open(file, "a", encoding="utf-8") as f:
            for line in data:
                f.write(line)
                f.write("\n")
    except OSError as e:
        print(f"Error writing to file {file}: {e}")
        exit(1)
    except Exception as e:
        print(f"Generic error: {e}")
        exit(1)


def open_file(file: Path):
    try:
        subprocess.run(["open", file], check=False)
    except Exception as e:
        print(f"Error opening file {file} to view: {e}")
        exit(1)
