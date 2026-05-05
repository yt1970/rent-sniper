from openai import OpenAI

client = OpenAI()


def generate_comment(room):
    prompt = f"""
    以下の賃貸物件（建物）情報を評価してください。
    短く一言コメントで。

    物件名: {room.get('name', '不明')}
    住所: {room.get('address', '不明')}
    空室状況: {room.get('status', '不明')}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        print("AI error:", e)
        return "評価生成に失敗"