import os
import subprocess
import tempfile
from output.format import clean_line

def output_to_file(results: dict, filename: str) -> None:
    is_temp = False

    if filename == "":
        file = tempfile.NamedTemporaryFile(delete=False)
        filename = file.name
        file.close()
        is_temp = True

    with open(filename, "w", encoding="utf-8") as f:
        for filepath, lines in results.items():
            f.write(f"\n=== {filepath} ===\n")
            for line in lines:
                cleaned = clean_line(line)
                f.write(cleaned + "\n")
            f.write("\n\n")

    if is_temp:
        response = input("View results? [y/n] ").strip().lower()
        if response == "y":
            subprocess.run(["open", filename], check=False)
        else:
            os.unlink(filename)