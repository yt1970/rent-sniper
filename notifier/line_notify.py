"""
line_notify.py - 本番用（環境変数から取得、dotenv対応）
ローカルで動かす場合は line_notify_local.py を使うこと
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")


def send_line(message: str):
    if not LINE_TOKEN:
        raise ValueError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")

    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messages": [{"type": "text", "text": message}]
    }

    res = requests.post(url, headers=headers, json=body)

    if res.status_code != 200:
        print(f"LINE error [{res.status_code}]: {res.text}")
    else:
        print("LINE: 通知送信完了")
