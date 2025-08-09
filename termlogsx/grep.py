import re
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List
from .parse import parse_line



def grep_search(file: Path, search: str, behind: int, ahead: int) -> Dict:
    file_results: dict = {}
    pattern: type[re.Pattern[str]] = re.Pattern[str]
    b_buffer: deque = deque(maxlen=behind)
    a_buffer: deque = deque()
    match_mode: bool = False
    match_group: int = 0

    try:
        with open(file, "r", encoding="utf-8") as f:
            group_results: list = [dict]
            for line in f:
                parsed = parse_line(line)
                if not parsed:
                    continue

                is_match = search.lower() in parsed["content"].lower()

                if not match_mode:

                    if not is_match:
                        b_buffer.append(parsed)
                        continue
                    if is_match:
                        match_mode = True
                        match_group += 1
                        parsed["match"] = True
                        group_results = list(b_buffer) + [parsed]
                        b_buffer.clear()
                        continue

                if match_mode:

                    if not is_match:
                        a_buffer.append(parsed)
                        if len(a_buffer) >= ahead:
                            group_results = group_results + list(a_buffer)
                            a_buffer.clear()
                            file_results[match_group] = group_results
                            match_mode = False
                        continue
                    if is_match:
                        group_results = group_results + list(a_buffer) + [parsed]
                        parsed["match"] = True
                        a_buffer.clear()
                        continue

        if len(a_buffer) > 0:
            group_results = group_results + list(a_buffer)
            file_results[match_group] = group_results

    except Exception as e:
        print(f"Failure in {file}: {e}")

    return file_results
