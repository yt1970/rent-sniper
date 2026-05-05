# 🚀 rent-sniper 運用・セットアップガイド

初心者向けの完全手順書です。  
「GitHubって何？」から「自動実行まで」を一気通貫で説明します。

---

## 目次

1. [全体像](#1-全体像)
2. [GitHubのセットアップ](#2-githubのセットアップ)
3. [AWSのセットアップ](#3-awsのセットアップ)
4. [GitHub Secretsの登録](#4-github-secretsの登録)
5. [CI/CDの仕組みと定義](#5-cicdの仕組みと定義)
6. [動作確認](#6-動作確認)
7. [日常的な使い方（Gitのマナー）](#7-日常的な使い方gitのマナー)
8. [トラブルシューティング](#8-トラブルシューティング)

---

## 1. 全体像

```
あなたのMac（コード書く）
    │
    │ git push
    ▼
GitHub（コードを保管）
    │
    │ pushを検知 → 自動実行
    ▼
GitHub Actions（クラウドでPythonを実行）
    │
    ├── VillageHouseをスクレイピング
    ├── AWS S3から前回データ取得
    ├── 差分検知（新着・成約済み）
    └── LINEに通知
         │
         ▼
      あなたのLINE 📲
```

### 使っているサービス

| サービス | 役割 | 料金 |
|---|---|---|
| GitHub | コード保管・自動実行のトリガー | 無料 |
| GitHub Actions | クラウドでコードを自動実行 | 無料（月2,000分まで） |
| AWS S3 | 物件データの保存 | ほぼ無料（月数円以下） |
| AWS IAM | AWSの権限管理 | 無料 |
| LINE Messaging API | LINE通知の送信 | 無料 |

---

## 2. GitHubのセットアップ

### 2.1 アカウント作成

1. [github.com](https://github.com) にアクセス
2. 「Sign up」からアカウント作成
3. メール認証を完了

### 2.2 リポジトリとは？

> フォルダのようなもの。プロジェクトのコードをまるごと保管する場所。

### 2.3 ローカル環境の初期設定

```bash
# Gitのユーザー情報を設定（初回のみ）
git config --global user.name "あなたの名前"
git config --global user.email "your@email.com"
```

### 2.4 リポジトリをクローン（初回のみ）

```bash
git clone https://github.com/yt1970/rent-sniper.git
cd rent-sniper
```

---

## 3. AWSのセットアップ

### 3.1 AWSアカウントについて

> AWSはクラウドサービス。今回はデータ保存（S3）だけに使う。

⚠️ **重要**: 管理者権限（ルートアカウント）のキーは絶対にGitHubに置かない。  
必ず**専用のIAMユーザー**を作って最小権限だけ付与すること。

### 3.2 S3バケットの作成

S3（Simple Storage Service）= クラウド上のフォルダ。

1. AWSコンソール → S3 → 「バケットを作成」
2. 設定：
   - バケット名: `rent-sniper-data`
   - リージョン: `アジアパシフィック（東京） ap-northeast-1`
   - それ以外: **全部デフォルトのまま**
3. 「バケットを作成」をクリック

### 3.3 IAMユーザーの作成

IAM（Identity and Access Management）= AWSの権限管理。  
「このユーザーはS3のこのバケットしか触れない」という設定をする。

**手順①: ポリシー（権限の定義）を作る**

1. IAM → ポリシー → 「ポリシーを作成」
2. JSONタブを選択して以下を貼り付け：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::rent-sniper-data",
        "arn:aws:s3:::rent-sniper-data/*"
      ]
    }
  ]
}
```

3. ポリシー名: `rent-sniper-s3-policy`
4. 「ポリシーを作成」

**手順②: ユーザーを作る**

1. IAM → ユーザー → 「ユーザーを作成」
2. ユーザー名: `rent-sniper-github-actions`
3. コンソールアクセス: **不要**（チェックしない）
4. 「ポリシーを直接アタッチ」→ `rent-sniper-s3-policy` を選択
5. 「ユーザーを作成」

**手順③: アクセスキーを発行する**

1. 作成したユーザーをクリック
2. 「セキュリティ認証情報」タブ
3. 「アクセスキーを作成」
4. ユースケース: 「サードパーティサービス」を選択
5. **CSVをダウンロード**（この画面を閉じると二度と見れない！）

CSVの中身：
```
Access key ID,Secret access key
AKIAXXXXXXXXXXXXXXXX,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 4. GitHub Secretsの登録

> Secretsとは：APIキーなどの機密情報をGitHubに安全に保存する仕組み。  
> コードには書かず、実行時だけ環境変数として渡される。

### 登録手順

1. GitHubリポジトリ → Settings → Secrets and variables → Actions
2. 「New repository secret」を6回繰り返す

| Secret名 | 値 |
|---|---|
| `AWS_ACCESS_KEY_ID` | CSVの左側の値（`AKIA`で始まる） |
| `AWS_SECRET_ACCESS_KEY` | CSVの右側の値（長い文字列） |
| `AWS_DEFAULT_REGION` | `ap-northeast-1` |
| `S3_BUCKET` | `rent-sniper-data` |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE DevelopersのChannel access token |
| `LINE_USER_ID` | LINEのユーザーID（`U`で始まる） |

---

## 5. CI/CDの仕組みと定義

### CI/CDとは？

- **CI（Continuous Integration）**: コードをpushするたびに自動でテストを実行する仕組み
- **CD（Continuous Deployment）**: テストが通ったら自動でデプロイ（本番反映）する仕組み

rent-sniperでは「pushのたびに自動でスクレイピングを実行」= CDとして使っている。

### ワークフローファイル（`.github/workflows/snipe.yml`）

```yaml
name: rent-sniper

on:
  schedule:
    - cron: '0 23 1,15 * *'  # 毎月1日・15日 朝8時（JST）
  push:
    branches:
      - main                  # mainへのpush時に自動実行
  workflow_dispatch:           # 手動実行ボタン
```

#### cronの読み方

```
┌─ 分（0〜59）
│  ┌─ 時（0〜23）※UTC
│  │  ┌─ 日（1〜31）
│  │  │     ┌─ 月（1〜12）
│  │  │     │  ┌─ 曜日（0〜7）
│  │  │     │  │
0  23  1,15  *  *

→ 毎月1日と15日の23時（UTC）= 日本時間 翌朝8時
```

#### キャッシュの仕組み

Playwrightのブラウザは毎回インストールすると2〜3分かかる。  
キャッシュを使うと2回目以降はスキップされて高速化できる。

```yaml
- name: Cache Playwright browsers
  uses: actions/cache@v4
  id: playwright-cache
  with:
    path: ~/.cache/ms-playwright
    key: playwright-chromium-${{ runner.os }}

- name: Install Playwright browsers
  if: steps.playwright-cache.outputs.cache-hit != 'true'  # キャッシュなし時のみ実行
  run: playwright install chromium --with-deps

- name: Install Playwright system deps only
  if: steps.playwright-cache.outputs.cache-hit == 'true'  # キャッシュあり時はdepsのみ
  run: playwright install-deps chromium
```

---

## 6. 動作確認

### 手動実行

1. GitHubリポジトリ → Actions タブ
2. 左側の「rent-sniper」をクリック
3. 「Run workflow」→ 緑の「Run workflow」ボタン
4. 実行中のジョブをクリックしてログを確認

### ログの見方

```
✅ 正常終了の場合
new rooms: 0, sold rooms: 0
LINE: 通知送信完了

❌ エラーの場合
botocore.errorfactory.AccessDenied: ...
→ IAMの権限不足。ポリシーを確認する。
```

### LINE通知パターン

| 状況 | 通知内容 |
|---|---|
| 新着物件あり | 🏠 新着空室情報！（物件詳細） |
| 成約済みあり | 🔒 成約済みになりました（物件詳細） |
| 変化なし | 🏠 新着なし |

---

## 7. 日常的な使い方（Gitのマナー）

### 基本的な流れ

```bash
# 1. 作業前は必ずpullする（リモートの最新を取り込む）
git pull origin main

# 2. コードを編集する
# ...

# 3. 変更をステージングする
git add .

# 4. コミットする（変更の記録）
git commit -m "feat: フィルタ機能追加"

# 5. pushする（GitHubに反映・Actionsが自動実行される）
git push origin main
```

### コミットメッセージのルール

わかりやすいメッセージを書く習慣をつけると、後で見返したときに便利。

| プレフィックス | 意味 | 例 |
|---|---|---|
| `feat:` | 新機能追加 | `feat: 成約済み検知追加` |
| `fix:` | バグ修正 | `fix: LINE通知のエラー修正` |
| `docs:` | ドキュメント更新 | `docs: README更新` |
| `refactor:` | リファクタリング | `refactor: main.py整理` |
| `chore:` | 雑務・設定変更 | `chore: requirements.txt更新` |

### ⚠️ やってはいけないこと

```bash
# ❌ 絶対にやらない
# .envファイルをgit addしない（APIキーが漏れる）
git add .env  # ← NG

# ✅ .gitignoreで除外されているか確認
cat .gitignore
```

### .gitignoreに必ず入れるもの

```
.env
venv/
__pycache__/
*.pyc
rooms.json   # ローカルのデータファイル
```

### MCPとローカルを併用するときの注意

Claude Desktop（MCP）でファイルを書き換えた場合は、  
**必ずpullしてからローカルで作業すること**。

```bash
# MCPでファイルを変更した後は必ず
git pull origin main

# その後に作業 → add → commit → push
```

---

## 8. トラブルシューティング

### push時に rejected されたとき

```
error: failed to push some refs
hint: Updates were rejected because the remote contains work
```

→ リモートが先に進んでいる。pullしてからpushする。

```bash
git pull origin main --no-rebase
git push origin main
```

### コンフリクトが起きたとき

```
CONFLICT (content): Merge conflict in xxx.py
```

→ 同じファイルをローカルとリモートで両方変更した。

```bash
# ローカル版を採用する場合
git checkout --ours ファイル名

# リモート版を採用する場合
git checkout --theirs ファイル名

git add ファイル名
git commit -m "merge: コンフリクト解消"
git push origin main
```

### vimが開いてしまったとき

```
# 保存して終了
:wq

# 保存せずに終了
:q!
```

### GitHub ActionsでAccessDeniedエラー

```
botocore.errorfactory.AccessDenied
```

→ IAMポリシーの権限が足りない。以下を確認：
- `s3:GetObject` / `s3:PutObject` / `s3:ListBucket` の3つが設定されているか
- Resourceに `rent-sniper-data` と `rent-sniper-data/*` の両方があるか

### Secretsが効いていないとき

→ Secret名のタイポを確認（大文字小文字・アンダースコア）  
→ Secretを変更した場合はActionsを再実行する

---

## 参考リンク

- [GitHub Actions 公式ドキュメント](https://docs.github.com/ja/actions)
- [AWS S3 公式ドキュメント](https://docs.aws.amazon.com/ja_jp/s3/)
- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)
- [Playwright ドキュメント](https://playwright.dev/python/)
