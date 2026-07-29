#!/usr/bin/env python3
"""
Generates a neofetch-style GitHub profile README stats block.
Pulls live data from the GitHub API and writes it into README.md
between the START_SECTION / END_SECTION markers.

Requires env var: GH_TOKEN (a GitHub Personal Access Token or the
built-in GITHUB_TOKEN from Actions) and GH_USERNAME.
"""

import os
import sys
import requests
from datetime import datetime, timezone

USERNAME = os.environ.get("GH_USERNAME")
TOKEN = os.environ.get("GH_TOKEN")

if not USERNAME or not TOKEN:
    print("Missing GH_USERNAME or GH_TOKEN env vars.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

API = "https://api.github.com"


def get_user():
    r = requests.get(f"{API}/users/{USERNAME}", headers=HEADERS)
    r.raise_for_status()
    return r.json()


def get_all_repos():
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"{API}/users/{USERNAME}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page, "type": "owner"},
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_languages(repos):
    """Aggregate bytes-of-code per language across all owned repos."""
    lang_totals = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        r = requests.get(repo["languages_url"], headers=HEADERS)
        if r.status_code != 200:
            continue
        for lang, count in r.json().items():
            lang_totals[lang] = lang_totals.get(lang, 0) + count
    # sort by usage, take top languages
    return sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)


def compute_stars(repos):
    return sum(repo.get("stargazers_count", 0) for repo in repos)


def compute_uptime(created_at: str):
    created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    now = datetime.now(timezone.utc)
    delta = now - created
    years = delta.days // 365
    remaining_days = delta.days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    return f"{years} years, {months} months, {days} days"


def build_block(user, repos, languages):
    stars = compute_stars(repos)
    uptime = compute_uptime(user["created_at"])
    top_langs = ", ".join(lang for lang, _ in languages[:5]) or "N/A"

    lines = []
    lines.append(f"{USERNAME}@github " + "-" * 40)
    lines.append(f". Uptime: {'.' * 20} {uptime}")
    lines.append(f". Public Repos: {'.' * 15} {user.get('public_repos', 0)}")
    lines.append(f". Followers: {'.' * 19} {user.get('followers', 0)}")
    lines.append(f". Following: {'.' * 19} {user.get('following', 0)}")
    lines.append("")
    lines.append(f". Top Languages: {'.' * 14} {top_langs}")
    lines.append("")
    lines.append(f"- GitHub Stats -" + "-" * 30)
    lines.append(f". Repos: {'.' * 22} {user.get('public_repos', 0)}")
    lines.append(f". Stars: {'.' * 22} {stars}")
    lines.append(f". Followers: {'.' * 18} {user.get('followers', 0)}")
    lines.append(
        f". Last updated: {'.' * 14} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

    return "```\n" + "\n".join(lines) + "\n```"


def update_readme(block):
    path = "README.md"
    start_marker = "<!-- STATS_START -->"
    end_marker = "<!-- STATS_END -->"

    if not os.path.exists(path):
        content = f"# Hi, I'm {USERNAME}!\n\n{start_marker}\n{block}\n{end_marker}\n"
    else:
        with open(path, "r") as f:
            content = f.read()

        if start_marker in content and end_marker in content:
            before = content.split(start_marker)[0]
            after = content.split(end_marker)[1]
            content = f"{before}{start_marker}\n{block}\n{end_marker}{after}"
        else:
            content += f"\n\n{start_marker}\n{block}\n{end_marker}\n"

    with open(path, "w") as f:
        f.write(content)


def main():
    user = get_user()
    repos = get_all_repos()
    languages = get_languages(repos)
    block = build_block(user, repos, languages)
    update_readme(block)
    print("README.md updated successfully.")


if __name__ == "__main__":
    main()
