"""Generate wide terminal-style profile SVG with two-column layout."""
import html
import json
import os
import urllib.request
from datetime import date

USER = "saltuwwa"
BORN = date(2007, 11, 28)

def uptime() -> str:
    today = date.today()
    years = today.year - BORN.year - ((today.month, today.day) < (BORN.month, BORN.day))
    months_total = (today.year - BORN.year) * 12 + today.month - BORN.month
    if today.day < BORN.day:
        months_total -= 1
    months = months_total - years * 12
    m = BORN.month + months_total
    anchor = date(BORN.year + (m - 1) // 12, (m - 1) % 12 + 1, BORN.day)
    days = (today - anchor).days
    return f"{years} years, {months} months, {days} days"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def gh_stats():
    u = fetch(f"https://api.github.com/users/{USER}")
    repos = fetch(f"https://api.github.com/users/{USER}/repos?per_page=100")
    stars = sum(r["stargazers_count"] for r in repos)
    return u["public_repos"], stars, u["followers"]

# ================================================================ SVG

C = {
    "bg":     "#0d1117",
    "border": "#30363d",
    "label":  "#ffa657",   # orange
    "prompt": "#ffa657",   # orange for user
    "at":     "#8b949e",   # gray @
    "host":   "#7ee787",   # green
    "dots":   "#3d444d",   # dark dots
    "val":    "#e6edf3",   # light gray values
    "num":    "#79c0ff",   # blue for numbers
    "sect":   "#d2a8ff",   # purple for section titles
}

# Font sizes (px)
FONT_PROMPT = 18      # prompt line
FONT_SECTION = 16     # "System", "Profile"
FONT_TEXT = 17        # main content
FONT_LABEL = 16       # field names

# Spacing
LINE_HEIGHT = 24
PAD = 40
COL_WIDTH = 420
COL_GAP = 60
TOTAL_WIDTH = PAD + COL_WIDTH + COL_GAP + COL_WIDTH + PAD

# SVG dimensions
SVG_WIDTH = TOTAL_WIDTH
SVG_HEIGHT = 480


def make_svg(up, n_repos, n_stars, n_followers):
    """Build wide terminal-style SVG with two columns."""
    out = []
    
    # SVG header
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" '
        f'font-family="\'JetBrains Mono\',\'Fira Code\',\'Cascadia Code\',Menlo,monospace" '
        f'style="white-space:pre; overflow: visible;">'
    )
    
    # Background
    out.append(
        f'<rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="12" '
        f'fill="{C["bg"]}" stroke="{C["border"]}" stroke-width="2"/>'
    )
    
    # Subtle top glow effect (optional)
    out.append(
        f'<defs><linearGradient id="glow" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" style="stop-color:{C["border"]};stop-opacity:0.3"/>'
        f'<stop offset="100%" style="stop-color:{C["bg"]};stop-opacity:0"/>'
        f'</linearGradient></defs>'
    )
    out.append(
        f'<rect width="{SVG_WIDTH}" height="80" rx="12" fill="url(#glow)"/>'
    )
    
    y = PAD
    
    # ============ Prompt line
    prompt_text = f"{USER}@github:~$ "
    out.append(
        f'<text x="{PAD}" y="{y}" font-size="{FONT_PROMPT}" font-weight="bold" '
        f'font-family="\'JetBrains Mono\',monospace">'
        f'<tspan fill="{C["prompt"]}">{html.escape(USER)}</tspan>'
        f'<tspan fill="{C["at"]}">@</tspan>'
        f'<tspan fill="{C["host"]}">github</tspan>'
        f'<tspan fill="{C["val"]}">::~$</tspan>'
        f'</text>'
    )
    
    y += LINE_HEIGHT + 10
    
    # Separator line
    out.append(
        f'<line x1="{PAD}" y1="{y}" x2="{SVG_WIDTH - PAD}" y2="{y}" '
        f'stroke="{C["border"]}" stroke-width="1" opacity="0.5"/>'
    )
    
    y += LINE_HEIGHT - 5
    
    # ============ LEFT COLUMN: System
    x_left = PAD
    
    # Section title
    out.append(
        f'<text x="{x_left}" y="{y}" font-size="{FONT_SECTION}" '
        f'fill="{C["sect"]}" font-weight="bold">System</text>'
    )
    y += LINE_HEIGHT + 5
    
    # System fields
    system_lines = [
        ("OS", "Windows 11"),
        ("Host", "SDU, Kazakhstan"),
        ("Uptime", up),
        ("Kernel", "CS student"),
        ("Shell", "PowerShell, Git Bash"),
        ("IDE", "VS Code, Claude Code"),
    ]
    
    for label, value in system_lines:
        # Label
        out.append(
            f'<text x="{x_left}" y="{y}" font-size="{FONT_TEXT}" '
            f'fill="{C["label"]}" font-family="monospace">{html.escape(label)}</text>'
        )
        
        # Dots
        label_width = len(label) * 10
        dots_x = x_left + label_width + 8
        out.append(
            f'<text x="{dots_x}" y="{y}" font-size="{FONT_TEXT}" '
            f'fill="{C["dots"]}" font-family="monospace">........</text>'
        )
        
        # Value
        val_x = dots_x + 70
        val_color = C["num"] if label == "Uptime" else C["val"]
        out.append(
            f'<text x="{val_x}" y="{y}" font-size="{FONT_TEXT}" '
            f'fill="{val_color}" font-family="monospace">{html.escape(value)}</text>'
        )
        
        y += LINE_HEIGHT
    
    # ============ RIGHT COLUMN: Profile
    x_right = x_left + COL_WIDTH + COL_GAP
    y_right = PAD + 35  # Align with System title
    
    # Section title
    out.append(
        f'<text x="{x_right}" y="{y_right}" font-size="{FONT_SECTION}" '
        f'fill="{C["sect"]}" font-weight="bold">Profile</text>'
    )
    y_right += LINE_HEIGHT + 5
    
    # Profile fields
    profile_lines = [
        ("Programming", "Python, Java, TypeScript"),
        ("Computer", "SQL, HTML/CSS, LaTeX, JSON"),
        ("Languages", "Kazakh, Russian, English"),
        ("Focus", "LLM agents, RAG, fine-tuning"),
        ("Hobbies", "badminton, hiking, 3Blue1Brown"),
    ]
    
    for label, value in profile_lines:
        # Label
        out.append(
            f'<text x="{x_right}" y="{y_right}" font-size="{FONT_TEXT}" '
            f'fill="{C["label"]}" font-family="monospace">{html.escape(label)}</text>'
        )
        
        # Dots
        label_width = len(label) * 10
        dots_x = x_right + label_width + 8
        out.append(
            f'<text x="{dots_x}" y="{y_right}" font-size="{FONT_TEXT}" '
            f'fill="{C["dots"]}" font-family="monospace">........</text>'
        )
        
        # Value
        val_x = dots_x + 70
        out.append(
            f'<text x="{val_x}" y="{y_right}" font-size="{FONT_TEXT}" '
            f'fill="{C["val"]}" font-family="monospace">{html.escape(value)}</text>'
        )
        
        y_right += LINE_HEIGHT
    
    out.append('</svg>')
    return '\n'.join(out)


def main():
    try:
        n_repos, n_stars, n_followers = gh_stats()
    except Exception as e:
        print(f"API error: {e}")
        n_repos, n_stars, n_followers = 25, 4, 6
    
    svg = make_svg(uptime(), n_repos, n_stars, n_followers)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    
    print(f"✓ profile.svg ({SVG_WIDTH}×{SVG_HEIGHT}) | uptime: {uptime()} | stats: {n_repos} repos, {n_stars} stars")


if __name__ == "__main__":
    main()
