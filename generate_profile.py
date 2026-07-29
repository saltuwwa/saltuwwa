#!/usr/bin/env python3
"""Generate profile.svg with dynamic uptime."""
import html
from datetime import date

USER = "saltuwwa"
BORN = date(2007, 11, 28)

# Colors
C = {
    "bg":     "#0d1117",
    "border": "#30363d",
    "user":   "#ffa657",   # orange
    "host":   "#7ee787",   # green
    "prompt": "#8b949e",   # gray
    "sect":   "#d2a8ff",   # purple
    "label":  "#ffa657",   # orange
    "dots":   "#484f58",   # dark gray
    "val":    "#e6edf3",   # light gray
    "uptime": "#79c0ff",   # blue
}

FONT_PROMPT = 18
FONT_SECTION = 16
FONT_TEXT = 16
LINE_HEIGHT = 25

PAD = 32
MAX_WIDTH = 600  # single column, not too wide


def uptime() -> str:
    """Calculate uptime."""
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


def text_line(x, y, text, fill, size, bold=False):
    """Create SVG text element."""
    weight = 'font-weight="bold"' if bold else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'font-family="monospace" {weight}>{html.escape(text)}</text>'
    )


def make_svg():
    """Build single-column profile SVG."""
    out = []
    
    y = PAD
    x = PAD
    
    # SVG dimensions (calculate from content)
    # prompt + separator + system (6 lines) + profile (5 lines) + gaps = ~340px
    svg_height = 430
    svg_width = int(PAD + MAX_WIDTH + PAD)
    
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" '
        f'viewBox="0 0 {svg_width} {svg_height}" '
        f'font-family="\'JetBrains Mono\',\'Cascadia Code\',Menlo,monospace" '
        f'style="white-space:pre;">'
    )
    
    # Background
    out.append(
        f'<rect width="{svg_width}" height="{svg_height}" rx="10" '
        f'fill="{C["bg"]}" stroke="{C["border"]}" stroke-width="2"/>'
    )
    
    # Prompt line
    out.append(text_line(x, y, f"{USER}@github:~$", C["user"], FONT_PROMPT, bold=True))
    y += LINE_HEIGHT + 8
    
    # Separator
    out.append(
        f'<line x1="{x}" y1="{y}" x2="{svg_width - PAD}" y2="{y}" '
        f'stroke="{C["border"]}" stroke-width="1" opacity="0.5"/>'
    )
    y += LINE_HEIGHT
    
    # System section
    out.append(text_line(x, y, "System", C["sect"], FONT_SECTION, bold=True))
    y += LINE_HEIGHT
    
    system_fields = [
        ("OS", "Windows 11"),
        ("Host", "SDU, Kazakhstan"),
        ("Uptime", uptime()),
        ("Kernel", "CS student"),
        ("Shell", "PowerShell, Git Bash"),
        ("IDE", "VS Code, Claude Code"),
    ]
    
    for label, value in system_fields:
        # Label
        out.append(text_line(x, y, label, C["label"], FONT_TEXT))
        
        # Dots
        dots_x = x + len(label) * 10 + 12
        dot_count = 17 - len(label)
        dots = "." * dot_count
        out.append(text_line(dots_x, y, dots, C["dots"], FONT_TEXT))
        
        # Value
        val_x = dots_x + dot_count * 10 + 8
        val_color = C["uptime"] if label == "Uptime" else C["val"]
        out.append(text_line(val_x, y, value, val_color, FONT_TEXT))
        
        y += LINE_HEIGHT
    
    y += 8
    
    # Profile section
    out.append(text_line(x, y, "Profile", C["sect"], FONT_SECTION, bold=True))
    y += LINE_HEIGHT
    
    profile_fields = [
        ("Programming", "Python, Java, TypeScript, JavaScript"),
        ("Computer", "SQL, HTML/CSS, LaTeX, JSON"),
        ("Languages", "Kazakh, Russian, English"),
        ("Focus", "LLM agents, RAG, fine-tuning, NLP"),
        ("Hobbies", "badminton, hiking, 3Blue1Brown marathons"),
    ]
    
    for label, value in profile_fields:
        # Label
        out.append(text_line(x, y, label, C["label"], FONT_TEXT))
        
        # Dots
        dots_x = x + len(label) * 10 + 12
        dot_count = 17 - len(label)
        dots = "." * dot_count
        out.append(text_line(dots_x, y, dots, C["dots"], FONT_TEXT))
        
        # Value
        val_x = dots_x + dot_count * 10 + 8
        out.append(text_line(val_x, y, value, C["val"], FONT_TEXT))
        
        y += LINE_HEIGHT
    
    out.append('</svg>')
    return '\n'.join(out)


def main():
    svg = make_svg()
    with open("profile.svg", "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"Generated profile.svg | uptime: {uptime()}")


if __name__ == "__main__":
    main()
