"""Rebuild README.md: recompute uptime and fetch live GitHub stats.

Runs daily via .github/workflows/update-readme.yml.
"""
import json
import os
import urllib.request
from datetime import date

USER = "saltuwwa"
BORN = date(2007, 11, 28)
ART_W = 44

# ASCII art generated from the profile photo (static)
ART = """\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@%#%%@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@%=:.   .-*%@@@@@@@@@@@@@@#**
@@@@@@@@@@@@@@@*. :::::   :*@@@@@@@@@@%#*+++
@@@@@@@@@@@@@@%==******+=:  +@@@@@@%##***+++
@@@@@@@@@@@@@@*+#****++++*=. %@@@@#####*+++=
@@@@@@@@@@@@@%.++--+*+==+#%+.-@@%#####***+=-
@@@@@@@@@@@@@# =#*+*##*#%%%*- *%%######**++=
@@@@@@@@@@@@@# :##*******##+. -%%###***+++++
@@@@@@@@@@@@@%. :+##*+*#%#*:   #%####*===+==
@@@@@@@@@@@@%%:  :=*####*=.    -#%##*++**+=-
@@@@@@@@@@%**#.     =**+=:      :#####*#*+++
@@@%@@@%+:  .:.     :+**+:       :-+***#**++
@@@**##-              -=:            .+###*+
%%##*%-                                =##+=
-**+*+                                  =+==
=*#**.                           ::     .=++
+***=                           .*#.     -++
:--*-                           .--.     =+=
:--+-                                    *##
+++::                                    #@@
##*-.                                    #@%
%%+:.                                    %@@
%%#:                                    .%@%
###:                                    :%%#
###.                                    =%%%"""


def uptime() -> str:
    today = date.today()
    years = today.year - BORN.year - ((today.month, today.day) < (BORN.month, BORN.day))
    months_total = (today.year - BORN.year) * 12 + today.month - BORN.month
    if today.day < BORN.day:
        months_total -= 1
    months = months_total - years * 12
    m = BORN.month + months_total
    anchor = date(BORN.year + (m - 1) // 12, (m - 1) % 12 + 1, min(BORN.day, 28))
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


def main():
    try:
        n_repos, n_stars, n_followers = gh_stats()
    except Exception:
        n_repos, n_stars, n_followers = 25, 4, 6  # fallback if API is down

    info = [
        f"{USER}@github",
        "-" * 33,
        "OS ........... Windows 11",
        "Host ......... SDU, Kazakhstan",
        f"Uptime ....... {uptime()}",
        "Kernel ....... CS student, 1st year",
        "Shell ........ PowerShell, Git Bash",
        "IDE .......... VS Code, Claude Code",
        "",
        "Languages.Programming .. Python, Java,",
        "                         TypeScript, JS",
        "Languages.Computer ..... SQL, HTML/CSS,",
        "                         LaTeX, JSON",
        "Languages.Real ......... Kazakh, Russian,",
        "                         English",
        "",
        "Focus.AI ..... LLM agents, RAG,",
        "               fine-tuning, NLP",
        "Hobbies ...... badminton, hiking,",
        "               3Blue1Brown marathons",
        "",
        "Contact:",
        "  LinkedIn ... in/saltanat-tugayeva-057305387",
        "  X .......... x.com/tsaltanatt",
        f"  GitHub ..... {USER}",
        "",
        "GitHub Stats:",
        f"  Repos {n_repos} | Stars {n_stars} | Followers {n_followers}",
    ]

    art_lines = ART.split("\n")
    rows = max(len(art_lines), len(info))
    art_lines += [""] * (rows - len(art_lines))
    info += [""] * (rows - len(info))
    body = "\n".join(f"{a:<{ART_W + 3}}{i}".rstrip() for a, i in zip(art_lines, info))

    readme = f"""```text
{body}
```

[LinkedIn](https://www.linkedin.com/in/saltanat-tugayeva-057305387/) · [X / Twitter](https://x.com/tsaltanatt)

# \U0001f4ca GitHub Stats:
![](https://github-readme-stats.vercel.app/api?username={USER}&theme=dark&hide_border=false&include_all_commits=false&count_private=false)<br/>
![](https://github-readme-stats.vercel.app/api/top-langs/?username={USER}&theme=dark&hide_border=false&include_all_commits=false&count_private=false&layout=compact)
"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(readme)
    print("README updated | uptime:", uptime(), "| stats:", n_repos, n_stars, n_followers)


if __name__ == "__main__":
    main()
