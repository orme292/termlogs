import re
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List
from .parse import parse_line


def grep_search(file: Path, search: str, behind: int, ahead: int, regex: bool = False, match_case: bool = False) -> Dict:
    file_results: dict = {}
    pattern: re.Pattern
    b_buffer: deque = deque(maxlen=behind)
    a_buffer: deque = deque()
    match_mode: bool = False
    match_group: int = 0

    if regex:
        try:
            pattern = re.compile(search)
        except re.error as e:
            raise ValueError(f"Regex error: {e}")

    try:
        with open(file, "r", encoding="utf-8") as f:
            group_results: list = [dict]
            for line in f:
                parsed = parse_line(line)
                if not parsed:
                    continue

                if regex:
                    is_match = pattern.search(parsed["content"]) is not None
                else:
                    if match_case:
                        is_match = search in parsed["content"]
                    else:
                        is_match = search.lower() in parsed["content"].casefold()


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
        raise Exception(f"Error {file}: {e}")

    return file_results
