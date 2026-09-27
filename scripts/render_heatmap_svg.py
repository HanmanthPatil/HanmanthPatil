import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("assets/contrib-heatmap.svg")

CELL = 12
GAP = 4
STEP = CELL + GAP

COLORS = {
    0: "#161b22",
    1: "#12343b",
    2: "#155e63",
    3: "#0891b2",
    4: "#67e8f9",
}

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_calendar(days):
    if not days:
        return []

    # GitHub contribution calendars are arranged Sunday → Saturday.
    # Pad the beginning so the first date starts on the correct weekday.
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    padding = (first_date.weekday() + 1) % 7

    cells = [{"empty": True}] * padding

    for day in days:
        cells.append({
            "empty": False,
            "date": day["date"],
            "count": day["count"],
            "level": min(day["level"], 4),
        })

    return cells


def render_svg(data):
    days = data.get("days", [])
    stats = data.get("stats", {})

    cells = build_calendar(days)

    weeks = (len(cells) + 6) // 7

    chart_x = 36
    chart_y = 72

    chart_width = weeks * STEP
    chart_height = 7 * STEP

    width = chart_x + chart_width + 30
    height = chart_y + chart_height + 48

    rects = []

    for index, cell in enumerate(cells):
        if cell.get("empty"):
            continue

        week = index // 7
        day = index % 7

        x = chart_x + week * STEP
        y = chart_y + day * STEP

        color = COLORS.get(cell["level"], COLORS[0])

        rects.append(
            f'''
            <rect
                x="{x}"
                y="{y}"
                width="{CELL}"
                height="{CELL}"
                rx="3"
                fill="{color}"
                opacity="0">
                <title>{cell["date"]} — {cell["count"]} contributions</title>
                <animate
                    attributeName="opacity"
                    values="0;1"
                    dur="0.35s"
                    begin="{index * 0.008}s"
                    fill="freeze"/>
            </rect>
            '''
        )

    total = stats.get("total_contributions", 0)
    active = stats.get("days_with_activity", 0)
    best = stats.get("best_day", 0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}">

    <defs>
        <linearGradient id="cyanGlow" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#67e8f9"/>
            <stop offset="100%" stop-color="#0891b2"/>
        </linearGradient>

        <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>

    <rect
        x="0"
        y="0"
        width="{width}"
        height="{height}"
        rx="14"
        fill="#0b0f14"
        stroke="#1f2937"/>

    <text
        x="24"
        y="30"
        fill="#f8fafc"
        font-family="monospace"
        font-size="14"
        font-weight="700">
        GITHUB ACTIVITY
    </text>

    <text
        x="24"
        y="50"
        fill="#64748b"
        font-family="monospace"
        font-size="9">
        {total:,} contributions · {active} active days · peak {best}
    </text>

    <line
        x1="24"
        y1="58"
        x2="{width - 24}"
        y2="58"
        stroke="#1f2937"/>

    {''.join(rects)}

    <text
        x="{chart_x}"
        y="{height - 14}"
        fill="#475569"
        font-family="monospace"
        font-size="8">
        LESS
    </text>

    <rect x="{chart_x + 32}" y="{height - 21}" width="9" height="9" rx="2" fill="{COLORS[0]}"/>
    <rect x="{chart_x + 46}" y="{height - 21}" width="9" height="9" rx="2" fill="{COLORS[1]}"/>
    <rect x="{chart_x + 60}" y="{height - 21}" width="9" height="9" rx="2" fill="{COLORS[2]}"/>
    <rect x="{chart_x + 74}" y="{height - 21}" width="9" height="9" rx="2" fill="{COLORS[3]}"/>
    <rect x="{chart_x + 88}" y="{height - 21}" width="9" height="9" rx="2" fill="{COLORS[4]}"/>

    <text
        x="{chart_x + 105}"
        y="{height - 14}"
        fill="#475569"
        font-family="monospace"
        font-size="8">
        MORE
    </text>

    </svg>
    '''

    return svg


def main():
    data = load_data()
    svg = render_svg(data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(svg)

    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
