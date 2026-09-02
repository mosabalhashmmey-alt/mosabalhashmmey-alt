import os
import json
import html
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict


# ============================================================
# MUSSAB // LIVE ENGINE
# GitHub data → dynamically generated SVG
# ============================================================

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "mosabalhashmmey-alt")
TOKEN = os.getenv("GITHUB_TOKEN", "")

OUTPUT_FILE = Path(".github/assets/live-engine.svg")

API_BASE = "https://api.github.com"

SAUDI_TZ = timezone(timedelta(hours=3))


# ============================================================
# GITHUB API
# ============================================================

def github_get(endpoint):
    url = f"{API_BASE}{endpoint}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mussab-live-engine",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        print(f"[GitHub API] HTTP {error.code}: {url}")
        return None

    except Exception as error:
        print(f"[GitHub API] Error: {error}")
        return None


# ============================================================
# HELPERS
# ============================================================

def safe(value):
    return html.escape(str(value or ""), quote=True)


def truncate(text, length=42):
    text = str(text or "")

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def relative_time(value):
    date = parse_date(value)

    if not date:
        return "unknown"

    now = datetime.now(timezone.utc)
    delta = now - date

    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "just now"

    minutes = seconds // 60

    if minutes < 60:
        return f"{minutes}m ago"

    hours = minutes // 60

    if hours < 24:
        return f"{hours}h ago"

    days = hours // 24

    if days < 30:
        return f"{days}d ago"

    months = days // 30

    return f"{months}mo ago"


def event_description(event):
    event_type = event.get("type", "")
    repo_name = event.get("repo", {}).get("name", "unknown")

    short_repo = repo_name.split("/")[-1]

    payload = event.get("payload", {})

    if event_type == "PushEvent":
        commits = payload.get("commits", [])
        count = len(commits)

        if count == 1:
            return f"pushed 1 commit to {short_repo}"

        return f"pushed {count} commits to {short_repo}"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "repository")

        if ref_type == "repository":
            return f"created repository {short_repo}"

        return f"created {ref_type} in {short_repo}"

    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        return f"{action} pull request in {short_repo}"

    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        return f"{action} issue in {short_repo}"

    if event_type == "IssueCommentEvent":
        return f"commented in {short_repo}"

    if event_type == "ForkEvent":
        return f"forked {short_repo}"

    if event_type == "WatchEvent":
        return f"starred {short_repo}"

    if event_type == "ReleaseEvent":
        action = payload.get("action", "published")
        return f"{action} release in {short_repo}"

    return f"{event_type.replace('Event', '')} activity in {short_repo}"


# ============================================================
# LOAD USER DATA
# ============================================================

print(f"[LIVE ENGINE] Loading GitHub data for @{USERNAME}...")


user = github_get(f"/users/{USERNAME}") or {}

repos = github_get(
    f"/users/{USERNAME}/repos"
    "?per_page=100"
    "&sort=pushed"
    "&direction=desc"
    "&type=owner"
) or []

events = github_get(
    f"/users/{USERNAME}/events/public?per_page=100"
) or []


# ============================================================
# PROFILE METRICS
# ============================================================

public_repo_count = user.get("public_repos", len(repos))
followers = user.get("followers", 0)

owned_repos = [
    repo for repo in repos
    if not repo.get("fork", False)
]

latest_repo = None

if owned_repos:
    latest_repo = max(
        owned_repos,
        key=lambda repo: repo.get("created_at", "")
    )


latest_repo_name = (
    latest_repo.get("name", "No repository")
    if latest_repo
    else "No repository"
)

latest_repo_time = (
    relative_time(latest_repo.get("created_at"))
    if latest_repo
    else "—"
)


# ============================================================
# LATEST ACTIVITY
# ============================================================

latest_event = events[0] if events else None

if latest_event:
    latest_activity = event_description(latest_event)
    latest_activity_time = relative_time(latest_event.get("created_at"))
else:
    latest_activity = "No recent public activity"
    latest_activity_time = "—"


# ============================================================
# COMMITS IN LAST 30 DAYS
# Uses recent public PushEvent data.
# ============================================================

now_utc = datetime.now(timezone.utc)
thirty_days_ago = now_utc - timedelta(days=30)

recent_commits = 0

for event in events:

    if event.get("type") != "PushEvent":
        continue

    created_at = parse_date(event.get("created_at"))

    if not created_at:
        continue

    if created_at >= thirty_days_ago:
        recent_commits += len(
            event.get("payload", {}).get("commits", [])
        )


# ============================================================
# ACTIVE REPOSITORIES
# Activity = pushed during last 30 days.
# ============================================================

active_repositories = 0

for repo in owned_repos:

    pushed_at = parse_date(repo.get("pushed_at"))

    if pushed_at and pushed_at >= thirty_days_ago:
        active_repositories += 1


# ============================================================
# TOP LANGUAGE
# We inspect language byte totals across recent repositories.
# ============================================================

language_totals = defaultdict(int)

language_repo_limit = min(len(owned_repos), 20)

for repo in owned_repos[:language_repo_limit]:

    full_name = repo.get("full_name")

    if not full_name:
        continue

    languages = github_get(
        f"/repos/{full_name}/languages"
    ) or {}

    for language, bytes_count in languages.items():
        language_totals[language] += bytes_count


if language_totals:
    top_language = max(
        language_totals,
        key=language_totals.get
    )
else:
    top_language = "N/A"


# ============================================================
# LAST TRANSMISSIONS
# ============================================================

transmissions = []

for event in events:

    text = event_description(event)

    if text not in transmissions:
        transmissions.append(text)

    if len(transmissions) == 3:
        break


while len(transmissions) < 3:
    transmissions.append("waiting for next transmission...")


# ============================================================
# ACTIVITY SIGNAL SCORES
#
# These are visual indicators derived from actual account data.
# They are intentionally capped at 100.
# ============================================================

code_score = min(100, recent_commits * 6)

project_score = min(
    100,
    active_repositories * 18
)

ship_score = min(
    100,
    recent_commits * 4 + active_repositories * 12
)

explore_score = min(
    100,
    len(owned_repos) * 7
)


def bar_width(score, maximum=260):
    return int((score / 100) * maximum)


# ============================================================
# LAST SYNC
# ============================================================

sync_time = datetime.now(SAUDI_TZ).strftime(
    "%Y-%m-%d %H:%M UTC+03"
)


# ============================================================
# SVG
# ============================================================

svg = f"""
<svg
    width="1200"
    height="590"
    viewBox="0 0 1200 590"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
>

<defs>

    <linearGradient
        id="background"
        x1="0"
        y1="0"
        x2="1200"
        y2="590"
        gradientUnits="userSpaceOnUse"
    >
        <stop offset="0%" stop-color="#020617"/>
        <stop offset="38%" stop-color="#071126"/>
        <stop offset="72%" stop-color="#18143F"/>
        <stop offset="100%" stop-color="#082F49"/>
    </linearGradient>

    <linearGradient
        id="neon"
        x1="0"
        y1="0"
        x2="1200"
        y2="0"
    >
        <stop offset="0%" stop-color="#22D3EE"/>
        <stop offset="45%" stop-color="#3B82F6"/>
        <stop offset="72%" stop-color="#8B5CF6"/>
        <stop offset="100%" stop-color="#38BDF8"/>
    </linearGradient>

    <linearGradient
        id="bar"
        x1="0"
        y1="0"
        x2="1"
        y2="0"
    >
        <stop offset="0%" stop-color="#0EA5E9"/>
        <stop offset="100%" stop-color="#8B5CF6"/>
    </linearGradient>

    <radialGradient
        id="radarGlow"
        cx="0"
        cy="0"
        r="1"
        gradientUnits="userSpaceOnUse"
        gradientTransform="translate(962 265) rotate(90) scale(200)"
    >
        <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.25"/>
        <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>

    <linearGradient
        id="radarSweep"
        x1="0"
        y1="0"
        x2="1"
        y2="1"
    >
        <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.75"/>
        <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </linearGradient>

    <pattern
        id="grid"
        width="28"
        height="28"
        patternUnits="userSpaceOnUse"
    >
        <path
            d="M28 0 L0 0 0 28"
            fill="none"
            stroke="#64748B"
            stroke-opacity="0.08"
        />
    </pattern>

    <filter
        id="glow"
        x="-60%"
        y="-60%"
        width="220%"
        height="220%"
    >
        <feGaussianBlur
            stdDeviation="3"
            result="blur"
        />

        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>

</defs>


<!-- ===================================================== -->
<!-- BACKGROUND -->
<!-- ===================================================== -->

<rect
    width="1200"
    height="590"
    rx="26"
    fill="url(#background)"
/>

<rect
    width="1200"
    height="590"
    rx="26"
    fill="url(#grid)"
/>

<rect
    x="1"
    y="1"
    width="1198"
    height="588"
    rx="25"
    fill="none"
    stroke="url(#neon)"
    stroke-opacity="0.55"
    stroke-width="2"
/>

<rect
    width="1200"
    height="3"
    fill="url(#neon)"
    filter="url(#glow)"
/>


<!-- ===================================================== -->
<!-- HEADER -->
<!-- ===================================================== -->

<text
    x="60"
    y="52"
    fill="#8B5CF6"
    font-family="monospace"
    font-size="14"
    letter-spacing="2"
>
    MUSSAB // LIVE ENGINE
</text>

<text
    x="60"
    y="93"
    fill="#FFFFFF"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="38"
    font-weight="700"
>
    REAL-TIME DEVELOPMENT SIGNAL
</text>

<text
    x="62"
    y="121"
    fill="#94A3B8"
    font-family="monospace"
    font-size="13"
>
    GitHub activity → parsed → analyzed → rendered
</text>


<rect
    x="950"
    y="48"
    width="184"
    height="34"
    rx="17"
    fill="#06101F"
    stroke="#22D3EE"
    stroke-opacity="0.25"
/>

<circle
    cx="974"
    cy="65"
    r="5"
    fill="#22C55E"
    filter="url(#glow)"
>
    <animate
        attributeName="opacity"
        values="1;0.3;1"
        dur="1.5s"
        repeatCount="indefinite"
    />
</circle>

<text
    x="990"
    y="69"
    fill="#CBD5E1"
    font-family="monospace"
    font-size="12"
>
    LIVE DATA
</text>


<!-- ===================================================== -->
<!-- LATEST ACTIVITY -->
<!-- ===================================================== -->

<rect
    x="58"
    y="150"
    width="705"
    height="116"
    rx="20"
    fill="#040A18"
    fill-opacity="0.68"
    stroke="#22D3EE"
    stroke-opacity="0.15"
/>

<text
    x="82"
    y="180"
    fill="#64748B"
    font-family="monospace"
    font-size="11"
    letter-spacing="1"
>
    LATEST ACTIVITY
</text>

<text
    x="82"
    y="215"
    fill="#F8FAFC"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="24"
    font-weight="650"
>
    {safe(truncate(latest_activity, 52))}
</text>

<text
    x="82"
    y="242"
    fill="#38BDF8"
    font-family="monospace"
    font-size="12"
>
    {safe(latest_activity_time)}
</text>


<!-- ===================================================== -->
<!-- RADAR -->
<!-- ===================================================== -->

<rect
    x="787"
    y="150"
    width="347"
    height="272"
    rx="20"
    fill="#040A18"
    fill-opacity="0.65"
    stroke="#8B5CF6"
    stroke-opacity="0.16"
/>

<rect
    x="787"
    y="150"
    width="347"
    height="272"
    rx="20"
    fill="url(#radarGlow)"
/>

<text
    x="812"
    y="180"
    fill="#64748B"
    font-family="monospace"
    font-size="11"
    letter-spacing="1"
>
    ACTIVITY RADAR
</text>

<circle
    cx="960"
    cy="290"
    r="95"
    fill="none"
    stroke="#22D3EE"
    stroke-opacity="0.20"
/>

<circle
    cx="960"
    cy="290"
    r="70"
    fill="none"
    stroke="#8B5CF6"
    stroke-opacity="0.18"
/>

<circle
    cx="960"
    cy="290"
    r="44"
    fill="none"
    stroke="#22D3EE"
    stroke-opacity="0.15"
/>

<line
    x1="865"
    y1="290"
    x2="1055"
    y2="290"
    stroke="#CBD5E1"
    stroke-opacity="0.10"
/>

<line
    x1="960"
    y1="195"
    x2="960"
    y2="385"
    stroke="#CBD5E1"
    stroke-opacity="0.10"
/>


<g transform="translate(960 290)">

    <path
        d="M0 0 L0 -93 A93 93 0 0 1 80 -47 Z"
        fill="url(#radarSweep)"
    >
        <animateTransform
            attributeName="transform"
            type="rotate"
            from="0"
            to="360"
            dur="5s"
            repeatCount="indefinite"
        />
    </path>

    <line
        x1="0"
        y1="0"
        x2="0"
        y2="-92"
        stroke="#22D3EE"
        stroke-width="2"
        filter="url(#glow)"
    >
        <animateTransform
            attributeName="transform"
            type="rotate"
            from="0"
            to="360"
            dur="5s"
            repeatCount="indefinite"
        />
    </line>

</g>


<circle
    cx="960"
    cy="290"
    r="6"
    fill="#FFFFFF"
    filter="url(#glow)"
/>

<circle cx="1007" cy="246" r="5" fill="#22D3EE" filter="url(#glow)">
    <animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/>
</circle>

<circle cx="1018" cy="323" r="5" fill="#8B5CF6" filter="url(#glow)">
    <animate attributeName="r" values="4;7;4" dur="2.4s" repeatCount="indefinite"/>
</circle>

<circle cx="916" cy="333" r="5" fill="#38BDF8" filter="url(#glow)">
    <animate attributeName="r" values="4;7;4" dur="1.8s" repeatCount="indefinite"/>
</circle>


<!-- ===================================================== -->
<!-- DATA CARDS -->
<!-- ===================================================== -->

<rect
    x="58"
    y="286"
    width="220"
    height="136"
    rx="18"
    fill="#040A18"
    fill-opacity="0.68"
    stroke="#8B5CF6"
    stroke-opacity="0.14"
/>

<text
    x="80"
    y="315"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
>
    LATEST REPOSITORY
</text>

<text
    x="80"
    y="348"
    fill="#F8FAFC"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="20"
    font-weight="650"
>
    {safe(truncate(latest_repo_name, 18))}
</text>

<text
    x="80"
    y="374"
    fill="#A5B4FC"
    font-family="monospace"
    font-size="11"
>
    created {safe(latest_repo_time)}
</text>

<text
    x="80"
    y="401"
    fill="#38BDF8"
    font-family="monospace"
    font-size="11"
>
    TOP LANGUAGE // {safe(top_language)}
</text>


<rect
    x="297"
    y="286"
    width="220"
    height="136"
    rx="18"
    fill="#040A18"
    fill-opacity="0.68"
    stroke="#22D3EE"
    stroke-opacity="0.14"
/>

<text
    x="319"
    y="315"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
>
    REPOSITORY SIGNAL
</text>

<text
    x="319"
    y="350"
    fill="#FFFFFF"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="27"
    font-weight="700"
>
    {public_repo_count}
</text>

<text
    x="361"
    y="349"
    fill="#94A3B8"
    font-family="monospace"
    font-size="11"
>
    PUBLIC REPOS
</text>

<text
    x="319"
    y="382"
    fill="#FFFFFF"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="22"
    font-weight="700"
>
    {active_repositories}
</text>

<text
    x="350"
    y="381"
    fill="#94A3B8"
    font-family="monospace"
    font-size="11"
>
    ACTIVE / 30D
</text>

<text
    x="319"
    y="405"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
>
    followers // {followers}
</text>


<rect
    x="536"
    y="286"
    width="227"
    height="136"
    rx="18"
    fill="#040A18"
    fill-opacity="0.68"
    stroke="#8B5CF6"
    stroke-opacity="0.14"
/>

<text
    x="558"
    y="315"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
>
    COMMIT SIGNAL
</text>

<text
    x="558"
    y="355"
    fill="#FFFFFF"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="34"
    font-weight="700"
>
    {recent_commits}
</text>

<text
    x="609"
    y="354"
    fill="#94A3B8"
    font-family="monospace"
    font-size="11"
>
    COMMITS
</text>

<text
    x="558"
    y="382"
    fill="#A5B4FC"
    font-family="monospace"
    font-size="11"
>
    public activity / 30 days
</text>

<text
    x="558"
    y="405"
    fill="#38BDF8"
    font-family="monospace"
    font-size="10"
>
    signal acquired
</text>


<!-- ===================================================== -->
<!-- ACTIVITY SIGNAL BARS -->
<!-- ===================================================== -->

<rect
    x="58"
    y="444"
    width="530"
    height="104"
    rx="18"
    fill="#040A18"
    fill-opacity="0.68"
    stroke="#22D3EE"
    stroke-opacity="0.13"
/>

<text
    x="80"
    y="470"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
    letter-spacing="1"
>
    SIGNAL MATRIX
</text>


<text x="80" y="493" fill="#CBD5E1" font-family="monospace" font-size="10">CODE</text>

<rect x="148" y="484" width="260" height="9" rx="5" fill="#172033"/>
<rect x="148" y="484" width="{bar_width(code_score)}" height="9" rx="5" fill="url(#bar)"/>

<text x="430" y="493" fill="#64748B" font-family="monospace" font-size="10">{code_score}%</text>


<text x="80" y="513" fill="#CBD5E1" font-family="monospace" font-size="10">PROJECTS</text>

<rect x="148" y="504" width="260" height="9" rx="5" fill="#172033"/>
<rect x="148" y="504" width="{bar_width(project_score)}" height="9" rx="5" fill="url(#bar)"/>

<text x="430" y="513" fill="#64748B" font-family="monospace" font-size="10">{project_score}%</text>


<text x="80" y="533" fill="#CBD5E1" font-family="monospace" font-size="10">SHIP</text>

<rect x="148" y="524" width="260" height="9" rx="5" fill="#172033"/>
<rect x="148" y="524" width="{bar_width(ship_score)}" height="9" rx="5" fill="url(#bar)"/>

<text x="430" y="533" fill="#64748B" font-family="monospace" font-size="10">{ship_score}%</text>


<!-- ===================================================== -->
<!-- LAST TRANSMISSION -->
<!-- ===================================================== -->

<rect
    x="610"
    y="444"
    width="524"
    height="104"
    rx="18"
    fill="#040A18"
    fill-opacity="0.68"
    stroke="#8B5CF6"
    stroke-opacity="0.14"
/>

<text
    x="632"
    y="470"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
    letter-spacing="1"
>
    LAST TRANSMISSIONS
</text>

<text
    x="632"
    y="494"
    fill="#E2E8F0"
    font-family="monospace"
    font-size="11"
>
    &gt; {safe(truncate(transmissions[0], 55))}
</text>

<text
    x="632"
    y="515"
    fill="#CBD5E1"
    font-family="monospace"
    font-size="11"
>
    &gt; {safe(truncate(transmissions[1], 55))}
</text>

<text
    x="632"
    y="536"
    fill="#94A3B8"
    font-family="monospace"
    font-size="11"
>
    &gt; {safe(truncate(transmissions[2], 55))}
</text>


<!-- ===================================================== -->
<!-- FOOTER -->
<!-- ===================================================== -->

<text
    x="61"
    y="574"
    fill="#475569"
    font-family="monospace"
    font-size="10"
>
    AUTO-GENERATED FROM GITHUB DATA
</text>

<text
    x="918"
    y="574"
    fill="#475569"
    font-family="monospace"
    font-size="10"
>
    LAST SYNC // {safe(sync_time)}
</text>

</svg>
"""


# ============================================================
# WRITE FILE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE.write_text(
    svg.strip(),
    encoding="utf-8"
)

print("")
print("[LIVE ENGINE] SVG generated successfully.")
print(f"[LIVE ENGINE] Output: {OUTPUT_FILE}")
print(f"[LIVE ENGINE] Latest activity: {latest_activity}")
print(f"[LIVE ENGINE] Top language: {top_language}")
print(f"[LIVE ENGINE] Recent commits: {recent_commits}")
print(f"[LIVE ENGINE] Active repositories: {active_repositories}")
