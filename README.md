# 🏠 RentSniper

VillageHouseの東京都内物件を定期巡回し、新規空室をLINEに通知するツール。
GitHub Actions で月2回自動実行、物件データは AWS S3 に永続化。

---

## 機能

- 🔍 スクレイピング（VillageHouse 一覧 → 詳細）
- 📊 差分検知（新規物件のみ抽出）
- 🤖 AIコメント生成（実装中）
- 📲 LINE通知

---

## クイックスタート（ローカル）

```bash
pip install -r requirements.txt
cp .env.example .env   # 環境変数を編集
python main.py
```

---

## 本番運用（GitHub Actions + AWS S3）

月2回（1日・15日 朝8時）自動実行。
詳細は [ARCHITECTURE.md](./ARCHITECTURE.md) を参照。

### 必要な GitHub Secrets

| Secret名 | 内容 |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM アクセスキー |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM シークレットキー |
| `AWS_DEFAULT_REGION` | `ap-northeast-1` |
| `S3_BUCKET` | `rent-sniper-data` |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE アクセストークン |
| `LINE_USER_ID` | LINE 通知先ユーザーID |

---

## ドキュメント

| ファイル | 内容 |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | アーキテクチャ・構成・AWS設定手順 |
| [細部設計.md](./細部設計.md) | モジュール詳細設計 |
