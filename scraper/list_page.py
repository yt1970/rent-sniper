import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.villagehouse.jp"
TARGET_AREAS = [
    {
        "name": "東京都",
        "url": BASE_URL + "/chintai/kanto/tokyo/",
        "path": "/chintai/kanto/tokyo/",
    },
    {
        "name": "佐賀県",
        "url": BASE_URL + "/chintai/kyushu/saga/",
        "path": "/chintai/kyushu/saga/",
    },
]


def get_property_links():
    links = set()

    for area in TARGET_AREAS:
        html = requests.get(area["url"], timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select("a[href]"):
            href = a.get("href")

            if not href:
                continue

            if area["path"] in href:
                if href.startswith("http"):
                    links.add(href)
                else:
                    links.add(BASE_URL + href)

    return list(links)
