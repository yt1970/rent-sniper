import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.villagehouse.jp"
LIST_URL = BASE_URL + "/chintai/kanto/tokyo/"


def get_property_links():
    html = requests.get(LIST_URL, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.select("a[href]"):
        href = a.get("href")

        if not href:
            continue

        if "/chintai/" in href and href.count("/") > 3:
            if href.startswith("http"):
                links.add(href)
            else:
                links.add(BASE_URL + href)

    return list(links)