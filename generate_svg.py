import requests
from datetime import datetime, timezone

USERNAME = "keyushhh"

# -------------------------
# Fetch GitHub Data
# -------------------------

user = requests.get(
    f"https://api.github.com/users/{USERNAME}"
).json()

repos = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
).json()

public_repos = user["public_repos"]
followers = user["followers"]
profile_url = user["html_url"]

stars = sum(repo.get("stargazers_count", 0) for repo in repos)

languages = {}

for repo in repos:
    lang = repo.get("language")
    if lang:
        languages[lang] = languages.get(lang, 0) + 1

top_languages = ", ".join(
    sorted(
        languages,
        key=languages.get,
        reverse=True
    )[:5]
)

# ------------------------------------
# You can replace this later using
# GitHub GraphQL if you want.
# ------------------------------------

commits = "1,130"
uptime = "3 years, 11 months"

updated = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

values = {
    "{{REPOS}}": str(public_repos),
    "{{STARS}}": str(stars),
    "{{FOLLOWERS}}": str(followers),
    "{{COMMITS}}": commits,
    "{{UPTIME}}": uptime,
    "{{LANGUAGES}}": top_languages,
    "{{PROFILE_URL}}": profile_url,
    "{{UPDATED}}": updated,
}

# -------------------------
# Replace placeholders
# -------------------------

for svg in ["dark_mode.svg", "light_mode.svg"]:

    with open(svg, "r", encoding="utf-8") as f:
        content = f.read()

    for key, value in values.items():
        content = content.replace(key, value)

    with open(svg, "w", encoding="utf-8") as f:
        f.write(content)

print("SVGs updated successfully.")
