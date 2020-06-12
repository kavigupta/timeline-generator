import csv
from sys import argv
from datetime import datetime
from collections import defaultdict

import io

from urllib.request import urlopen

SHEET_ID = "19xUK5tN_PVhm6b-CyYZ3nZTwmfNtmS6MbikNQJWVN3k"

TIMELINE_DATA = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv&id={0}&gid=0".format(SHEET_ID)

OVERALL = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{w}"
    height="{h}"
    viewBox="{x0} {y0} {w} {h}"
    version="1.1">
<rect x="-100000" y="-100000" width="1000000" height="1000000" fill="#222" />

{content}
</svg>
""".strip()

TEXT = """
<text
   xml:space="preserve"
     x="{x}"
     y="{y}"
     font-size="{size}"
     style="font-family:sans-serif;fill:{color}">{text}</text>
"""

RECTANGLE = """
<rect x="{x}" y="{y}" width="{w}" height= "{h}" fill="{color}"/>
"""

CATEGORIES = {
    "War": "f88",
    "Primary": "8f8",
    "Politics": "88f",
    "Covid": "fe8",
    "BLM": "8ff",
    "Misc": "888"
}

START = datetime(2020, 1, 1)


def load_timeline():
    with urlopen(TIMELINE_DATA) as f:
        data = f.read().decode('utf-8')
    header, *data = list(csv.reader(io.StringIO(data)))

    assert header == ["Date", "Category", "Headline"]

    by_date = defaultdict(list)

    for date, category, headline in data:
        date = datetime.strptime(date + "/2020", "%m/%d/%Y")
        headline = datetime.strftime(date, "%b %d: ") + headline
        date = (date - START).days
        category = CATEGORIES[category]
        by_date[date].append((category, headline))
    return by_date


def main():

    by_date = load_timeline()
    height = 50
    content = []

    for date in sorted(by_date):
        k = len(by_date[date])
        for i, (color, headline) in enumerate(by_date[date]):
            used_height = min(1 / k, 0.5) * 0.8 * height
            content.append(
                TEXT.format(
                    color="#" + color,
                    x=0,
                    y=(i * 0.8 / k + 0.2 + date) * height,
                    text=headline,
                    size=used_height,
                )
            )

    content.append(RECTANGLE.format(x=-height, y=-height/2, w=height / 5, h=height * 366, color="white"))
    for month in range(1, 12 + 1):
        start = (datetime(2020, month, 1) - START).days - 1

        if month == 12:
            end = (datetime(2021, 1, 1) - START).days - 1
        else:
            end = (datetime(2020, month + 1, 1) - START).days - 1

        for ybase in start, end:
            content.append(RECTANGLE.format(x=-height * 3.5, y=(ybase + 0.5) * height, w=height * 3, h=height / 5, color="white"))

    with open(argv[1], "w") as f:
        w = 1200
        h = (366 + 1) * height + 5 * height
        f.write(
            OVERALL.format(
                content="".join(content),
                x0=-5 * height,
                y0=-5 * height,
                w=w + 5 * height,
                h=h + 5 * height,
            )
        )

main()
