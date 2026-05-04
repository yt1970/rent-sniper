from scraper.list_page import get_property_links
from scraper.detail_page import get_rooms
from storage.json_store import load_previous, save_current, diff_rooms
from notifier.line_notify import send_line
from ai.comment import generate_comment


def collect_all_rooms():
    links = get_property_links()
    all_rooms = []

    for link in links:
        try:
            rooms = get_rooms(link)
            all_rooms.extend(rooms)
        except Exception as e:
            print("error:", link, e)

    return all_rooms


def main():
    print("start collecting...")

    new_data = collect_all_rooms()
    old_data = load_previous()

    new_rooms = diff_rooms(old_data, new_data)

    print(f"new rooms: {len(new_rooms)}")

    for room in new_rooms[:5]:  # 通知多すぎ防止
        comment = generate_comment(room)

        message = f"""🏠 新着物件！

家賃: {room['rent']}
間取り: {room['layout']}
階: {room['floor']}

💬 {comment}

{room['url']}
"""
        send_line(message)

    save_current(new_data)


if __name__ == "__main__":
    main()