import re

def clean_line(line: str) -> str:
    # Collapse multiple spaces after '%' prompt
    return re.sub(r'(\]\s+)%\s+', r'\1% ', line)