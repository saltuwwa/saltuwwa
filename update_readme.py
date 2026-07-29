#!/usr/bin/env python3
"""Update README.md with current uptime between markers."""
import os
import re
from datetime import date

USER = "saltuwwa"
BORN = date(2007, 11, 28)
README_PATH = "README.md"
MARKER_START = "<!-- UPTIME:START -->"
MARKER_END = "<!-- UPTIME:END -->"


def uptime() -> str:
    """Calculate uptime as 'X years, Y months, Z days'."""
    today = date.today()
    years = today.year - BORN.year - ((today.month, today.day) < (BORN.month, BORN.day))
    months_total = (today.year - BORN.year) * 12 + today.month - BORN.month
    if today.day < BORN.day:
        months_total -= 1
    months = months_total - years * 12
    m = BORN.month + months_total
    anchor = date(BORN.year + (m - 1) // 12, (m - 1) % 12 + 1, BORN.day)
    days = (today - anchor).days
    return f"{years} years, {months} months, {days} day" + ("s" if days != 1 else "")


def update_readme():
    """Update uptime line in README.md between markers."""
    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found")
        return False
    
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_uptime = uptime()
    new_line = f"Uptime ............. {new_uptime}"
    
    # Replace content between markers
    pattern = f"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}"
    replacement = f"{MARKER_START}\n{new_line}\n{MARKER_END}"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Only write if content changed
    if new_content != content:
        with open(README_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print(f"Updated {README_PATH} | uptime: {new_uptime}")
        return True
    else:
        print(f"No changes | uptime: {new_uptime}")
        return False


if __name__ == "__main__":
    updated = update_readme()
    exit(0 if updated else 0)  # Always exit 0, let workflow check with git diff
