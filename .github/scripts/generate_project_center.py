import json
import html
from pathlib import Path


# ============================================================
# MUSSAB // PROJECT COMMAND CENTER
# projects.json → generated SVG
# ============================================================

DATA_FILE = Path(".github/data/projects.json")
OUTPUT_FILE = Path(".github/assets/project-command-center.svg")


# ============================================================
# HELPERS
# ============================================================

def safe(value):
    return html.escape(str(value or ""), quote=True)


def truncate(text, length=48):
    text = str(text or "")

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


def wrap_text(text, max_chars=58, max_lines=2):
    words = str(text or "").split()

    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)

            current = word

            if len(lines) >= max_lines:
                break

    if current and len(lines) < max_lines:
        lines.append(current)

    if len(lines) == max_lines:
        joined = " ".join(words)

        if len(" ".join(lines)) < len(joined):
            lines[-1] = truncate(lines[-1], max_chars - 1)

    return lines


def status_style(status):
    status = str(status or "").upper()

    styles = {
        "ACTIVE": {
            "color": "#22C55E",
            "stroke": "#22C55E",
            "label": "ACTIVE",
        },
        "SHIPPED": {
            "color": "#38BDF8",
            "stroke": "#38BDF8",
            "label": "SHIPPED",
        },
        "EXPERIMENT": {
            "color": "#A855F7",
            "stroke": "#A855F7",
            "label": "EXPERIMENT",
        },
        "PAUSED": {
            "color": "#F59E0B",
            "stroke": "#F59E0B",
            "label": "PAUSED",
        },
    }

    return styles.get(
        status,
        {
            "color": "#94A3B8",
            "stroke": "#94A3B8",
            "label": status or "UNKNOWN",
        },
    )


# ============================================================
# LOAD PROJECT DATA
# ============================================================

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Project data file not found: {DATA_FILE}"
    )


with DATA_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)


projects = data.get("projects", [])

featured_projects = [
    project
    for project in projects
    if project.get("featured", True)
]

# We show a maximum of 4 projects in the main command center.
featured_projects = featured_projects[:4]


# ============================================================
# SVG LAYOUT
# ============================================================

WIDTH = 1200
HEIGHT = 720

CARD_WIDTH = 515
CARD_HEIGHT = 220

LEFT_X = 65
RIGHT_X = 620

TOP_Y = 175
BOTTOM_Y = 425

positions = [
    (LEFT_X, TOP_Y),
    (RIGHT_X, TOP_Y),
    (LEFT_X, BOTTOM_Y),
    (RIGHT_X, BOTTOM_Y),
]


# ============================================================
# PROJECT CARDS
# ============================================================

cards_svg = []


for index, project in enumerate(featured_projects):

    x, y = positions[index]

    name = safe(
        truncate(
            project.get("name", "Untitled Project"),
            33,
        )
    )

    category = safe(
        truncate(
            project.get("category", "Project"),
            32,
        )
    )

    status = status_style(
        project.get("status", "")
    )

    description_lines = wrap_text(
        project.get("description", ""),
        max_chars=55,
        max_lines=2,
    )

    technologies = project.get(
        "technologies",
        [],
    )

    technologies = technologies[:4]

    tech_text = "  •  ".join(
        str(item)
        for item in technologies
    )

    tech_text = safe(
        truncate(
            tech_text,
            61,
        )
    )

    repository = project.get(
        "repository",
        "",
    )

    repo_name = (
        repository.rstrip("/").split("/")[-1]
        if repository
        else "repository unavailable"
    )

    repo_name = safe(
        truncate(
            repo_name,
            42,
        )
    )

    description_1 = (
        safe(description_lines[0])
        if len(description_lines) >= 1
        else ""
    )

    description_2 = (
        safe(description_lines[1])
        if len(description_lines) >= 2
        else ""
    )

    card = f"""
    <!-- PROJECT {index + 1} -->

    <g>

        <rect
            x="{x}"
            y="{y}"
            width="{CARD_WIDTH}"
            height="{CARD_HEIGHT}"
            rx="22"
            fill="#050A18"
            fill-opacity="0.72"
            stroke="url(#cardStroke)"
            stroke-opacity="0.34"
        />

        <rect
            x="{x + 1}"
            y="{y + 1}"
            width="{CARD_WIDTH - 2}"
            height="3"
            rx="2"
            fill="url(#neon)"
            opacity="0.8"
        />

        <!-- project index -->

        <text
            x="{x + 24}"
            y="{y + 34}"
            fill="#64748B"
            font-family="monospace"
            font-size="11"
            letter-spacing="1"
        >
            PROJECT NODE // {str(index + 1).zfill(2)}
        </text>

        <!-- status -->

        <rect
            x="{x + 385}"
            y="{y + 18}"
            width="105"
            height="28"
            rx="14"
            fill="#07111F"
            stroke="{status['stroke']}"
            stroke-opacity="0.38"
        />

        <circle
            cx="{x + 403}"
            cy="{y + 32}"
            r="4"
            fill="{status['color']}"
            filter="url(#glow)"
        >
            <animate
                attributeName="opacity"
                values="1;0.35;1"
                dur="{1.5 + (index * 0.25)}s"
                repeatCount="indefinite"
            />
        </circle>

        <text
            x="{x + 417}"
            y="{y + 36}"
            fill="{status['color']}"
            font-family="monospace"
            font-size="10"
            font-weight="700"
        >
            {safe(status['label'])}
        </text>

        <!-- project name -->

        <text
            x="{x + 24}"
            y="{y + 78}"
            fill="#F8FAFC"
            font-family="Segoe UI, Arial, sans-serif"
            font-size="25"
            font-weight="700"
        >
            {name}
        </text>

        <!-- category -->

        <text
            x="{x + 24}"
            y="{y + 103}"
            fill="#A78BFA"
            font-family="monospace"
            font-size="11"
        >
            {category}
        </text>

        <!-- description -->

        <text
            x="{x + 24}"
            y="{y + 133}"
            fill="#CBD5E1"
            font-family="Segoe UI, Arial, sans-serif"
            font-size="13"
        >
            {description_1}
        </text>

        <text
            x="{x + 24}"
            y="{y + 153}"
            fill="#94A3B8"
            font-family="Segoe UI, Arial, sans-serif"
            font-size="13"
        >
            {description_2}
        </text>

        <!-- technologies -->

        <text
            x="{x + 24}"
            y="{y + 183}"
            fill="#38BDF8"
            font-family="monospace"
            font-size="10"
        >
            {tech_text}
        </text>

        <!-- repository -->

        <text
            x="{x + 24}"
            y="{y + 205}"
            fill="#64748B"
            font-family="monospace"
            font-size="10"
        >
            github // {repo_name}
        </text>

    </g>
    """

    cards_svg.append(card)


# ============================================================
# EMPTY SLOTS
# ============================================================

for index in range(
    len(featured_projects),
    4,
):

    x, y = positions[index]

    empty_card = f"""
    <g opacity="0.42">

        <rect
            x="{x}"
            y="{y}"
            width="{CARD_WIDTH}"
            height="{CARD_HEIGHT}"
            rx="22"
            fill="#050A18"
            fill-opacity="0.52"
            stroke="#334155"
            stroke-opacity="0.30"
            stroke-dasharray="7 8"
        />

        <text
            x="{x + 24}"
            y="{y + 42}"
            fill="#475569"
            font-family="monospace"
            font-size="11"
        >
            PROJECT NODE // {str(index + 1).zfill(2)}
        </text>

        <text
            x="{x + 24}"
            y="{y + 105}"
            fill="#64748B"
            font-family="Segoe UI, Arial, sans-serif"
            font-size="22"
            font-weight="600"
        >
            Awaiting next project...
        </text>

        <text
            x="{x + 24}"
            y="{y + 135}"
            fill="#475569"
            font-family="monospace"
            font-size="11"
        >
            status // UNALLOCATED
        </text>

    </g>
    """

    cards_svg.append(empty_card)


cards_markup = "\n".join(cards_svg)


# ============================================================
# COUNTERS
# ============================================================

total_projects = len(projects)

active_count = sum(
    1
    for project in projects
    if str(project.get("status", "")).upper()
    == "ACTIVE"
)

shipped_count = sum(
    1
    for project in projects
    if str(project.get("status", "")).upper()
    == "SHIPPED"
)


# ============================================================
# FINAL SVG
# ============================================================

svg = f"""
<svg
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
>

<defs>

    <!-- ================================================= -->
    <!-- GRADIENTS -->
    <!-- ================================================= -->

    <linearGradient
        id="background"
        x1="0"
        y1="0"
        x2="1200"
        y2="720"
        gradientUnits="userSpaceOnUse"
    >
        <stop
            offset="0%"
            stop-color="#020617"
        />

        <stop
            offset="40%"
            stop-color="#071026"
        />

        <stop
            offset="72%"
            stop-color="#17143D"
        />

        <stop
            offset="100%"
            stop-color="#082F49"
        />
    </linearGradient>


    <linearGradient
        id="neon"
        x1="0"
        y1="0"
        x2="1200"
        y2="0"
    >
        <stop
            offset="0%"
            stop-color="#22D3EE"
        />

        <stop
            offset="42%"
            stop-color="#3B82F6"
        />

        <stop
            offset="72%"
            stop-color="#8B5CF6"
        />

        <stop
            offset="100%"
            stop-color="#38BDF8"
        />
    </linearGradient>


    <linearGradient
        id="cardStroke"
        x1="0"
        y1="0"
        x2="515"
        y2="220"
    >
        <stop
            offset="0%"
            stop-color="#22D3EE"
        />

        <stop
            offset="55%"
            stop-color="#3B82F6"
        />

        <stop
            offset="100%"
            stop-color="#8B5CF6"
        />
    </linearGradient>


    <!-- ================================================= -->
    <!-- GRID -->
    <!-- ================================================= -->

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
            stroke-width="1"
        />
    </pattern>


    <!-- ================================================= -->
    <!-- GLOW -->
    <!-- ================================================= -->

    <filter
        id="glow"
        x="-70%"
        y="-70%"
        width="240%"
        height="240%"
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


    <!-- ================================================= -->
    <!-- AMBIENT ORB -->
    <!-- ================================================= -->

    <radialGradient
        id="orb"
        cx="0"
        cy="0"
        r="1"
        gradientUnits="userSpaceOnUse"
        gradientTransform="translate(980 110) rotate(90) scale(300)"
    >
        <stop
            offset="0%"
            stop-color="#8B5CF6"
            stop-opacity="0.25"
        />

        <stop
            offset="100%"
            stop-color="#8B5CF6"
            stop-opacity="0"
        />
    </radialGradient>

</defs>


<!-- ===================================================== -->
<!-- BACKGROUND -->
<!-- ===================================================== -->

<rect
    width="1200"
    height="720"
    rx="28"
    fill="url(#background)"
/>

<rect
    width="1200"
    height="720"
    rx="28"
    fill="url(#grid)"
/>

<rect
    width="1200"
    height="720"
    rx="28"
    fill="url(#orb)"
/>

<rect
    x="1"
    y="1"
    width="1198"
    height="718"
    rx="27"
    fill="none"
    stroke="url(#neon)"
    stroke-opacity="0.52"
    stroke-width="2"
/>


<!-- ===================================================== -->
<!-- TOP SCANNER -->
<!-- ===================================================== -->

<rect
    x="-300"
    y="0"
    width="250"
    height="720"
    fill="#22D3EE"
    opacity="0.025"
    transform="skewX(-16)"
>
    <animate
        attributeName="x"
        values="-300;1450"
        dur="8s"
        repeatCount="indefinite"
    />
</rect>


<rect
    x="0"
    y="0"
    width="1200"
    height="3"
    fill="url(#neon)"
    filter="url(#glow)"
/>


<!-- ===================================================== -->
<!-- HEADER -->
<!-- ===================================================== -->

<text
    x="65"
    y="52"
    fill="#8B5CF6"
    font-family="monospace"
    font-size="14"
    letter-spacing="2"
>
    MUSSAB // PROJECT COMMAND CENTER
</text>


<text
    x="65"
    y="94"
    fill="#FFFFFF"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="38"
    font-weight="700"
>
    BUILD SYSTEMS. SHIP IDEAS.
</text>


<text
    x="67"
    y="122"
    fill="#94A3B8"
    font-family="monospace"
    font-size="13"
>
    PROJECT REGISTRY → STATUS MONITOR → TECHNOLOGY MATRIX
</text>


<!-- ===================================================== -->
<!-- COUNTERS -->
<!-- ===================================================== -->

<rect
    x="820"
    y="53"
    width="95"
    height="56"
    rx="15"
    fill="#050A18"
    fill-opacity="0.65"
    stroke="#22D3EE"
    stroke-opacity="0.20"
/>

<text
    x="840"
    y="75"
    fill="#64748B"
    font-family="monospace"
    font-size="9"
>
    PROJECTS
</text>

<text
    x="840"
    y="99"
    fill="#FFFFFF"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="22"
    font-weight="700"
>
    {total_projects}
</text>


<rect
    x="928"
    y="53"
    width="95"
    height="56"
    rx="15"
    fill="#050A18"
    fill-opacity="0.65"
    stroke="#22C55E"
    stroke-opacity="0.20"
/>

<text
    x="948"
    y="75"
    fill="#64748B"
    font-family="monospace"
    font-size="9"
>
    ACTIVE
</text>

<text
    x="948"
    y="99"
    fill="#22C55E"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="22"
    font-weight="700"
>
    {active_count}
</text>


<rect
    x="1036"
    y="53"
    width="99"
    height="56"
    rx="15"
    fill="#050A18"
    fill-opacity="0.65"
    stroke="#38BDF8"
    stroke-opacity="0.20"
/>

<text
    x="1055"
    y="75"
    fill="#64748B"
    font-family="monospace"
    font-size="9"
>
    SHIPPED
</text>

<text
    x="1055"
    y="99"
    fill="#38BDF8"
    font-family="Segoe UI, Arial, sans-serif"
    font-size="22"
    font-weight="700"
>
    {shipped_count}
</text>


<!-- ===================================================== -->
<!-- DIVIDER -->
<!-- ===================================================== -->

<line
    x1="65"
    y1="145"
    x2="1135"
    y2="145"
    stroke="url(#neon)"
    stroke-opacity="0.22"
/>


<!-- ===================================================== -->
<!-- PROJECT CARDS -->
<!-- ===================================================== -->

{cards_markup}


<!-- ===================================================== -->
<!-- FOOTER -->
<!-- ===================================================== -->

<line
    x1="65"
    y1="673"
    x2="1135"
    y2="673"
    stroke="url(#neon)"
    stroke-opacity="0.22"
/>


<circle
    cx="72"
    cy="698"
    r="4"
    fill="#22C55E"
    filter="url(#glow)"
>
    <animate
        attributeName="opacity"
        values="1;0.25;1"
        dur="1.6s"
        repeatCount="indefinite"
    />
</circle>


<text
    x="88"
    y="702"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
>
    PROJECT REGISTRY ONLINE
</text>


<text
    x="815"
    y="702"
    fill="#64748B"
    font-family="monospace"
    font-size="10"
>
    SOURCE // .github/data/projects.json
</text>

</svg>
"""


# ============================================================
# WRITE SVG
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE.write_text(
    svg.strip(),
    encoding="utf-8",
)


print("")
print("============================================")
print(" MUSSAB // PROJECT COMMAND CENTER")
print("============================================")
print("")
print(f"Projects loaded : {total_projects}")
print(f"Active projects : {active_count}")
print(f"Shipped projects: {shipped_count}")
print(f"Output          : {OUTPUT_FILE}")
print("")
print("Project Command Center generated successfully.")
