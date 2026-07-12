"""Generate profile.svg: ASCII portrait + colored neofetch-style info panel.

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

ART = """\
                x+**#%%##%
               .;*==+*x%%%#@
              ..........,x%%@
             *.............#%
             .x..,,.........*@
             .%;............=%
            ..##............%%%
            ..*#*..........#%%#
            ..+#%#:.......x%%%##
          %+..+x###x.....;x####x#
       %+++x*-*xxxxx*....-xx###x*%@@
      ,:****x*+*xxx*x#;:**xxx##xx##xx#@
     ..++*****++****x##%#xxxxx#*x######@
     .===+****=++**xxx###xxxxxx*x######x@
    .;====+***==****xxx##xxxxxx*x+*######
    .====++++*++******x##xx**xx**..#####x@
   #.=====+***+=+***x*x###**x***+=+######@
   ..===++**x*+=+*+*xx###x#xx****x##%%##x
  @,:+******x*=++++**x##%%%x*xxxx*x#%%###
  .;+xxxx*xx*+++++*xx##%%%%###%#####%####
  %=xxxxxx*******xx#%%%%%%%%%%%%#%%%##%%#
   #xx####xxxx##%%%%%%%%%@@@@@%%%%%%%%%%%
   #x#######%%@@@@@@@@@@@@@@@@@@@@@@@@@@@"""

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

# colors (GitHub-dark friendly, sunset theme to match the photo)
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
PAD = 26
ART_COLS = 44
GAP = 30


def line(label, dots, value, vcolor="val"):
    return [(label, "label"), (dots, "dots"), (value, vcolor)]


def build_info(up, n_repos, n_stars, n_followers):
    return [
        [(USER, "user"), ("@", "at"), ("github", "host")],
        [("-" * 34, "rule")],
        line("OS ", "........... ", "Windows 11"),
        line("Host ", "......... ", "SDU, Kazakhstan"),
        line("Uptime ", "....... ", up, "num"),
        line("Kernel ", "....... ", "CS student, 1st year"),
        line("Shell ", "........ ", "PowerShell, Git Bash"),
        line("IDE ", ".......... ", "VS Code, Claude Code"),
        [],
        line("Languages.Programming ", ".. ", "Python, Java,"),
        [(" " * 25, "val"), ("TypeScript, JS", "val")],
        line("Languages.Computer ", "..... ", "SQL, HTML/CSS,"),
        [(" " * 25, "val"), ("LaTeX, JSON", "val")],
        line("Languages.Real ", "......... ", "Kazakh, Russian,"),
        [(" " * 25, "val"), ("English", "val")],
        [],
        line("Focus.AI ", "..... ", "LLM agents, RAG,"),
        [(" " * 15, "val"), ("fine-tuning, NLP", "val")],
        line("Hobbies ", "...... ", "badminton, hiking,"),
        [(" " * 15, "val"), ("3Blue1Brown marathons", "val")],
        [],
        [("Contact:", "sect")],
        line("  LinkedIn ", "... ", "in/saltanat-tugayeva-057305387"),
        line("  X ", ".......... ", "x.com/tsaltanatt"),
        line("  GitHub ", "..... ", USER),
        [],
        [("GitHub Stats:", "sect")],
        [("  Repos ", "label"), (str(n_repos), "num"), ("  |  Stars ", "label"),
         (str(n_stars), "num"), ("  |  Followers ", "label"), (str(n_followers), "num")],
    ]


def make_svg(info):
    art_lines = ART.split("\n")
    rows = max(len(art_lines), len(info))
    width = int(PAD + ART_COLS * CH + GAP + 47 * CH + PAD)
    height = int(rows * LH + PAD * 2)
    x_info = PAD + ART_COLS * CH + GAP
    y0 = PAD + FONT

    art_top = PAD + max(0, (rows - len(art_lines)) * LH // 2)
    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="\'Cascadia Code\',Consolas,'
        f'\'DejaVu Sans Mono\',Menlo,monospace" font-size="{FONT}px" '
        f'style="white-space:pre">'
    )
    out.append(
        '<defs><linearGradient id="sunset" gradientUnits="userSpaceOnUse" '
        f'x1="0" x2="0" y1="{art_top}" y2="{art_top + len(art_lines) * LH}">'
        '<stop offset="0" stop-color="#ffe38e"/>'
        '<stop offset="0.45" stop-color="#ff9e64"/>'
        '<stop offset="1" stop-color="#f778ba"/>'
        "</linearGradient></defs>"
    )
    out.append(
        f'<rect width="{width}" height="{height}" rx="10" '
        f'fill="{C["bg"]}" stroke="{C["border"]}"/>'
    )

    # ascii portrait, vertically centered, sunset gradient
    art_y0 = art_top + FONT
    out.append('<g fill="url(#sunset)">')
    for i, l in enumerate(art_lines):
        if l:
            out.append(
                f'<text xml:space="preserve" x="{PAD}" y="{art_y0 + i * LH}">'
                f"{html.escape(l)}</text>"
            )
    out.append("</g>")

    # info panel
    for i, segs in enumerate(info):
        if not segs:
            continue
        spans = "".join(
            f'<tspan fill="{C[cls]}">{html.escape(txt)}</tspan>' for txt, cls in segs
        )
        bold = ' font-weight="bold"' if i == 0 else ""
        out.append(
            f'<text xml:space="preserve" x="{x_info}" y="{y0 + i * LH}"{bold}>'
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
