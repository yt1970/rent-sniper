import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.villagehouse.jp"


def get_all_detail_info(urls):
    """Playwrightでまとめて物件詳細ページから家賃・間取り・築年月を取得"""
    results = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for url in urls:
                rent = ""
                layout = ""
                built = ""

                try:
                    print(f"  Fetching details: {url}")
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")

                    # 物件情報が表示されるまで待つ
                    try:
                        page.wait_for_selector("h5", timeout=10000)
                    except Exception:
                        pass

                    html = page.content()
                    detail_soup = BeautifulSoup(html, "html.parser")

                    # 家賃（例: ¥73,400〜）
                    for tag in detail_soup.find_all("h5"):
                        t = tag.text.strip()
                        if re.match(r'[¥￥][\d,]+', t):
                            rent = t
                            break

                    # 間取り（例: 3DK）
                    for tag in detail_soup.find_all("h5"):
                        t = tag.text.strip()
                        if re.match(r'\d+[A-Z]+$', t):
                            layout = t
                            break

                    # 築年月（テーブル内「築年月」ラベルの隣）
                    for tag in detail_soup.find_all(string=re.compile(r'築年月')):
                        parent = tag.find_parent(["tr", "dl", "div"])
                        if parent:
                            cells = parent.find_all(["td", "dd", "span", "p"])
                            for cell in cells:
                                ct = cell.text.strip()
                                if re.match(r'\d{4}', ct):
                                    built = ct
                                    break
                            if built:
                                break

                    print(f"    rent={rent}, layout={layout}, built={built}")

                except Exception as e:
                    print(f"    Playwright error: {e}")

                results[url] = (rent, layout, built)

            browser.close()
    except Exception as e:
        print(f"  Playwright launch error: {e}")

    return results


def get_rooms(property_url):
    html = requests.get(property_url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    rooms = []

    # 一覧ページ内の建物カード（コミュニティ）を取得
    cards = soup.select("div.container-search-cards-community-wrap")

    # まず空室ありの物件URLを収集
    valid_cards = []
    for card in cards:
        title_tag = card.select_one("h3 a")
        status_tag = card.select_one(".container-search-cards-community-status b")

        if not title_tag:
            continue

        status = status_tag.text.strip() if status_tag else ""
        if status == "空室なし":
            continue

        href = title_tag["href"]
        if not href.startswith("http"):
            href = BASE_URL + href

        valid_cards.append((card, title_tag, status, href))

    # 空室ありの物件のみPlaywrightでまとめて詳細取得
    if valid_cards:
        urls = list(set(href for _, _, _, href in valid_cards))
        detail_info = get_all_detail_info(urls)
    else:
        detail_info = {}

    for card, title_tag, status, href in valid_cards:
        address_tag = card.select_one(".container-search-cards-community-area")
        line_tag = card.select_one(".container-search-cards-community-line")

        rent, layout, built = detail_info.get(href, ("", "", ""))

        room_id = property_url + "_" + title_tag.text.strip()

        rooms.append({
            "id": room_id,
            "name": title_tag.text.strip(),
            "url": href,
            "address": address_tag.text.strip() if address_tag else "",
            "line": line_tag.text.strip() if line_tag else "",
            "status": status,
            "rent": rent,
            "layout": layout,
            "built": built,
        })

        print("room:", rooms[-1])

    print(f"Found {len(rooms)} rooms in {property_url}")

    return rooms