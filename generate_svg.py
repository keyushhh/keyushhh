import requests
from datetime import datetime, timezone

USERNAME = "keyushhh"

USER_API = f"https://api.github.com/users/{USERNAME}"
REPOS_API = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

# --------------------------------------------------
# Fetch user information
# --------------------------------------------------

user_response = requests.get(USER_API, timeout=30)
user_response.raise_for_status()
user = user_response.json()

repos_response = requests.get(REPOS_API, timeout=30)
repos_response.raise_for_status()
repos = repos_response.json()

# --------------------------------------------------
# Basic Stats
# --------------------------------------------------

public_repos = user["public_repos"]
followers = user["followers"]
profile_url = user["html_url"]

stars = sum(repo.get("stargazers_count", 0) for repo in repos)

# --------------------------------------------------
# Top Languages
# --------------------------------------------------

languages = {}

for repo in repos:
    language = repo.get("language")
    if language:
        languages[language] = languages.get(language, 0) + 1

top_languages = ", ".join(
    sorted(
        languages,
        key=languages.get,
        reverse=True
    )[:5]
)

if not top_languages:
    top_languages = "N/A"

# --------------------------------------------------
# GitHub Account Uptime
# --------------------------------------------------

created = datetime.strptime(
    user["created_at"],
    "%Y-%m-%dT%H:%M:%SZ"
).replace(tzinfo=timezone.utc)

now = datetime.now(timezone.utc)

years = now.year - created.year
months = now.month - created.month

if months < 0:
    years -= 1
    months += 12

uptime = f"{years} years, {months} months"

# --------------------------------------------------
# Commits
# --------------------------------------------------
# GitHub REST API doesn't expose lifetime commit count.
# Replace this later with GraphQL if desired.

commits = "1,130"

# --------------------------------------------------
# Last Updated
# --------------------------------------------------

updated = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

# --------------------------------------------------
# Placeholder values
# --------------------------------------------------

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

# --------------------------------------------------
# Update SVG Templates
# --------------------------------------------------

for svg in [
    "dark_mode_template.svg",
    "light_mode_template.svg",
]:

    with open(svg, "r", encoding="utf-8") as file:
        content = file.read()

    for placeholder, value in values.items():
        content = content.replace(placeholder, value)

    with open(svg, "w", encoding="utf-8") as file:
        file.write(content)

print("✅ SVG templates updated successfully.")
