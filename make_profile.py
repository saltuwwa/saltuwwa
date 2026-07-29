"""Generate profile.svg: minimal terminal-style info panel without ASCII art.

Runs daily via .github/workflows/update-readme.yml — recomputes uptime
and pulls live repo/star/follower counts from the GitHub API.
"""
import html
import json
import os
import urllib.request
from datetime import date

USER = "saltuwwa"
BORN = date(2007, 11, 28)

# ---------------------------------------------------------------- data

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

# ---------------------------------------------------------------- svg

# colors (GitHub-dark friendly, terminal aesthetic)
C = {
    "bg":     "#0d1117",
    "border": "#30363d",
    "label":  "#ffa657",   # warm orange
    "dots":   "#3d444d",
    "val":    "#e6edf3",
    "sect":   "#d2a8ff",   # soft purple
    "num":    "#79c0ff",   # blue
    "user":   "#ffa657",
    "at":     "#8b949e",
    "host":   "#7ee787",   # green
    "rule":   "#30363d",
}

FONT = 13            # px, monospace
CH = FONT * 0.6      # approx char advance
LH = 17              # line height
PAD = 20


def line(label, dots, value, vcolor="val"):
    return [(label, "label"), (dots, "dots"), (value, vcolor)]


def build_info(up, n_repos, n_stars, n_followers):
    return [
        [(USER, "user"), ("@", "at"), ("github", "host")],
        [("-" * 46, "rule")],
        line("OS ", "..................... ", "Windows 11"),
        line("Host ", "................ ", "SDU, Kazakhstan"),
        line("Uptime ", ".............. ", up, "num"),
        line("Kernel ", ".............. ", "CS student, 1st year"),
        line("Shell ", "............... ", "PowerShell, Git Bash"),
        line("IDE ", ".................. ", "VS Code, Claude Code"),
        [],
        line("Languages.Programming ", " ", "Python, Java,"),
        [(" " * 25, "val"), ("TypeScript, JS", "val")],
        line("Languages.Computer ", " ... ", "SQL, HTML/CSS,"),
        [(" " * 25, "val"), ("LaTeX, JSON", "val")],
        line("Languages.Real ", " ......... ", "Kazakh, Russian,"),
        [(" " * 25, "val"), ("English", "val")],
        [],
        line("Focus.AI ", " ........... ", "LLM agents, RAG,"),
        [(" " * 15, "val"), ("fine-tuning, NLP", "val")],
        line("Hobbies ", " ............ ", "badminton, hiking,"),
        [(" " * 15, "val"), ("3Blue1Brown marathons", "val")],
        [],
        [("GitHub Stats:", "sect")],
        line("  Repos ", " ", (str(n_repos)).ljust(3), "num"),
        [("  |  ", "dots"), ("Stars ", "label"), (" ", "val"), (str(n_stars).ljust(3), "num"),
         ("  |  ", "dots"), ("Followers ", "label"), (" ", "val"), (str(n_followers).ljust(3), "num")],
    ]


def make_svg(info):
    rows = len(info)
    width = int(PAD + 52 * CH + PAD)
    height = int(rows * LH + PAD * 2)
    y0 = PAD + FONT

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="\'Cascadia Code\',\'Courier New\','
        f'\'DejaVu Sans Mono\',Menlo,monospace" font-size="{FONT}px" '
        f'style="white-space:pre">'
    )
    out.append(
        f'<rect width="{width}" height="{height}" rx="8" '
        f'fill="{C["bg"]}" stroke="{C["border"]}" stroke-width="1"/>'
    )

    # info panel only, no ASCII art
    for i, segs in enumerate(info):
        if not segs:
            continue
        spans = "".join(
            f'<tspan fill="{C[cls]}">{html.escape(txt)}</tspan>' for txt, cls in segs
        )
        bold = ' font-weight="bold"' if i == 0 else ""
        out.append(
            f'<text xml:space="preserve" x="{PAD}" y="{y0 + i * LH}"{bold}>'
            f"{spans}</text>"
        )

    out.append("</svg>")
    return "\n".join(out)


def main():
    try:
        n_repos, n_stars, n_followers = gh_stats()
    except Exception:
        n_repos, n_stars, n_followers = 25, 4, 6  # fallback if API is down
    svg = make_svg(build_info(uptime(), n_repos, n_stars, n_followers))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("profile.svg updated | uptime:", uptime(),
          "| stats:", n_repos, n_stars, n_followers)


if __name__ == "__main__":
    main()
