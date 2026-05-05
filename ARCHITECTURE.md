# 🏠 rent-sniper アーキテクチャ設計

## 概要

VillageHouseの東京都内物件を定期巡回し、新規空室を検知してLINE通知するツール。
GitHub Actions で月2回自動実行し、物件データは AWS S3 に永続化する。

---

## ディレクトリ構成

```
rent-sniper/
├── main.py                          # エントリーポイント
├── requirements.txt                 # 依存パッケージ
├── rooms.json                       # ローカル実行時の物件データ（S3使用時は不要）
├── .env                             # 環境変数（ローカル用・gitignore対象）
│
├── scraper/
│   ├── list_page.py                 # 一覧ページから物件URLを取得
│   └── detail_page.py              # 各物件ページから詳細情報を取得
│
├── storage/
│   ├── json_store.py                # S3対応版（本番用）
│   └── json_store_local.py         # ローカルファイル版（開発用）
│
├── notifier/
│   ├── line_notify.py               # LINE通知（本番用）
│   └── line_notify_local.py        # LINE通知ローカル版（開発用）
│
├── ai/
│   └── comment.py                  # AIコメント生成（実装中）
│
└── .github/
    └── workflows/
        └── snipe.yml               # GitHub Actions ワークフロー
```

---

## アーキテクチャ

```
GitHub Actions（月2回 cron: 1日・15日 朝8時）
        │
        ▼
    main.py 実行
        │
        ├── scraper/list_page.py     → 物件URL一覧取得
        │       │
        │       └── scraper/detail_page.py  → 物件詳細取得
        │
        ├── storage/json_store.py    → S3から前回データ取得
        │
        ├── 差分検知（新規物件のみ抽出）
        │
        ├── ai/comment.py           → AIコメント生成（実装中）
        │
        ├── notifier/line_notify.py → LINE通知送信
        │
        └── storage/json_store.py   → S3に最新データ保存
```

---

## 実行環境

| 環境 | ストレージ | 実行トリガー |
|---|---|---|
| ローカル | `rooms.json`（ファイル） | 手動 |
| 本番（GitHub Actions） | AWS S3 | cron（月2回）/ 手動dispatch |

---

## 環境変数

| 変数名 | 説明 | 必須 |
|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API のアクセストークン | ✅ |
| `LINE_USER_ID` | LINE 通知先のユーザーID | ✅ |
| `AWS_ACCESS_KEY_ID` | AWS IAM アクセスキー | 本番のみ |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM シークレットキー | 本番のみ |
| `AWS_DEFAULT_REGION` | AWSリージョン（`ap-northeast-1`） | 本番のみ |
| `S3_BUCKET` | S3バケット名（例: `rent-sniper-data`） | 本番のみ |
| `S3_KEY` | S3内のオブジェクトキー（`rooms.json`） | 本番のみ |

---

## GitHub Secrets 設定（本番デプロイ時）

GitHubリポジトリの `Settings > Secrets and variables > Actions` に以下を登録：

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION     → ap-northeast-1
S3_BUCKET              → rent-sniper-data
LINE_CHANNEL_ACCESS_TOKEN
LINE_USER_ID
```

---

## AWS構成

| サービス | 用途 | 補足 |
|---|---|---|
| S3 | 物件データの永続化 | バケット名: `rent-sniper-data` |
| IAM | GitHub Actions用の最小権限ユーザー | S3のGet/Putのみ許可 |

### IAM ポリシー（最小権限）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::rent-sniper-data/*"
    }
  ]
}
```

---

## ローカル実行

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

> ローカル実行時は `storage/json_store_local.py` を使うこと。

---

## 今後の拡張案

- [ ] AIコメント生成の有効化（`ai/comment.py`）
- [ ] フィルタ機能（家賃上限・駅距離）
- [ ] スコアリング
- [ ] SQLite / RDS によるDB化
- [ ] Web UI
- [ ] MCPサーバー化
