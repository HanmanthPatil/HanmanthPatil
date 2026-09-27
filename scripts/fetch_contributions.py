import json
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


USERNAME = "HanmanthPatil"
URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 GitHub-Profile-Contribution-Collector"
}


def fetch_page():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_contributions(html):
    soup = BeautifulSoup(html, "html.parser")

    days = []

    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")
        level = cell.get("data-level")

        if not date:
            continue

        try:
            count_text = cell.get("aria-label", "")
            match = re.search(r"([\d,]+) contribution", count_text)
            count = int(match.group(1).replace(",", "")) if match else 0
        except Exception:
            count = 0

        days.append({
            "date": date,
            "count": count,
            "level": int(level or 0)
        })

    return days


def build_stats(days):
    counts = [day["count"] for day in days]

    total = sum(counts)
    best_day = max(counts) if counts else 0

    return {
        "total_contributions": total,
        "best_day": best_day,
        "days_with_activity": sum(1 for count in counts if count > 0),
    }


def main():
    html = fetch_page()
    days = parse_contributions(html)

    data = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": build_stats(days),
    }

    with open("data/contributions.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(
        f"Collected {len(days)} contribution days "
        f"for {USERNAME}."
    )


if __name__ == "__main__":
    main()
