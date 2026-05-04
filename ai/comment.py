from openai import OpenAI

client = OpenAI()


def generate_comment(room):
    prompt = f"""
    以下の賃貸情報を評価してください。
    短く一言コメントで。

    家賃: {room['rent']}
    間取り: {room['layout']}
    階: {room['floor']}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        print("AI error:", e)
        return "評価生成に失敗"