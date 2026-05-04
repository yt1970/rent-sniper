import requests
from bs4 import BeautifulSoup


def get_rooms(property_url):
    html = requests.get(property_url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    rooms = []

    rows = soup.select("table tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 3:
            continue

        floor = cols[0].text.strip()
        layout = cols[1].text.strip()
        rent = cols[2].text.strip()

        room_id = f"{property_url}_{floor}_{layout}_{rent}"

        rooms.append({
            "id": room_id,
            "floor": floor,
            "layout": layout,
            "rent": rent,
            "url": property_url
        })

    return rooms