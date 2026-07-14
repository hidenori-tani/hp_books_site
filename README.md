# hp_books_site — hidenoritani.com 著書ページ自動生成

`outreach-books/marketing/books/*.md` の書籍メタデータから、
hidenoritani.com の **著書ページ** を自動生成し、Wix の iframe で表示するパイプライン。

**日本語（`index.html`）と英語（`en.html`）の2ページ**を出力し、各ページ上部の言語トグルで相互に行き来できる。
各シリーズ（カテゴリ）の表紙は**最大3冊まで**表示し、超過分は総数を併記して Amazon 著者ページへ誘導する。

**Wixの他ページ（ホーム/研究概要/研究業績/経歴/担当科目/連絡先 等）のレイアウトには一切触れない**
（このパイプラインが生成するのは著書一覧のHTML＝`index.html`／`en.html` のみ。Wixの英語ページとは別物）。

---

## アーキテクチャ

```
[新刊出版] → books/<slug>.md 追加
            ↓
       /kindle-update-hp
            ↓
   ┌────────────────────────────────────┐
   │ lib/generate.py                     │
   │  - books/*.md 読み込み              │
   │  - 日英のシリーズ別に分類           │
   │  - 各シリーズ(カテゴリ)表紙3冊まで  │
   │  - docs/index.html (日本語) 生成    │
   │  - docs/en.html   (英語)   生成     │
   └────────────────────────────────────┘
            ↓
        git push origin main
            ↓
   ┌────────────────────────────────────┐
   │ GitHub Pages                        │
   │  https://hidenori-tani.github.io/   │
   │    hp_books_site/        … 日本語    │
   │    hp_books_site/en.html … 英語      │
   └────────────────────────────────────┘
            ↓
   ┌────────────────────────────────────┐
   │ Wix「著書」ページの HTML iframe     │
   │ （src=…/hp_books_site/ = 日本語）   │
   │  ページ内の言語トグルで en.html へ  │
   └────────────────────────────────────┘
            ↓
        hidenoritani.com/books に反映
```

---

## ディレクトリ構成

```
hp_books_site/
├── README.md                    # このファイル
├── .gitignore
├── lib/
│   ├── generate.py              # HTML生成スクリプト
│   └── series_config.py         # シリーズ表示設定（順序・名前・配色）
└── docs/                        # ← GitHub Pages 公開ディレクトリ
    ├── index.html               # 日本語ページ（自動生成・手で編集しない）
    ├── en.html                  # 英語ページ（自動生成・手で編集しない）
    └── covers/                  # 表紙画像 <slug>.jpg（generate.py が自動同期）
```

> **日英2ページと表示ルール**
> - `index.html`＝日本語シリーズのみ／`en.html`＝英語シリーズのみ。`series_config.py` の各シリーズ `lang`（'jp'/'en'）で振り分ける。
> - 各ページ上部の言語トグル（日本語 ↔ English）で相互リンク。hero・フッターにも相互リンクを配置。
> - **各シリーズの表紙は最大3冊**（新しい順）。4冊以上は「全N冊（新着3冊を表示）」等と総数を併記。全著作は Amazon 著者ページへ誘導。

---

## 日常運用

新刊出版・レビュー更新があったとき：

```bash
/kindle-update-hp
```

これだけ。HTML再生成→commit→push→GitHub Pages 反映（1〜2分）→Wix iframe 自動更新。

オプション：
- `/kindle-update-hp --fetch` — 先に Amazon情報を全冊更新してから再生成（時間かかる）
- `/kindle-update-hp --no-push` — push せずローカル確認のみ

---

## 初回セットアップ（一度だけ）

### Step 1: GitHub リポジトリ作成

GitHub にログインして新規リポジトリを作成：
- Repository name: `hp_books_site`（または任意の名前）
- Public（GitHub Pages 無料プラン）
- README/`.gitignore` 追加せず空で作成

### Step 2: ローカルリポジトリと接続

```bash
cd /Users/tanihidenori/claude-work/outreach-books/hp_books_site
git branch -M main
git remote add origin git@github.com:<YOUR_GITHUB_USER>/hp_books_site.git
git push -u origin main
```

### Step 3: GitHub Pages 有効化

リポジトリの Settings → Pages：
- Source: **Deploy from a branch**
- Branch: `main` / Folder: `/docs`
- Save

1〜2分後、`https://<YOUR_GITHUB_USER>.github.io/hp_books_site/` でアクセス可能になります。

### Step 4: Wix 著書ページに iframe 設置

1. Wix エディタで「著書」ページを開く
2. **既存のコンテンツはそのまま** — ページ上部または下部に「+ 追加」→「埋め込み」→「HTML iFrame」を選択
3. ウィジェットのサイズを横幅 100% × 高さ 3000px 程度に設定
4. ウィジェットをクリック →「コードを入力」→ 以下を貼り付け：

```html
<iframe
  src="https://<YOUR_GITHUB_USER>.github.io/hp_books_site/"
  width="100%"
  height="3000"
  frameborder="0"
  scrolling="auto"
  style="border:none; display:block;">
</iframe>
```

5. プレビュー → 公開

**以降、Wix 側を触る必要は一切ありません。** すべて `/kindle-update-hp` で完結します。

> **日英2ページの見せ方**：上記の1つの iframe は日本語（`index.html`）を表示し、ページ内の「English」トグルを押すと iframe 内で `en.html` に切り替わる。**Wix側の追加作業は不要**。英語ページに直接着地させたい場合のみ、Wixの英語ページに `…/hp_books_site/en.html` を指す2つ目の iframe を任意で設置する。各ページは分割で短くなったので、iframe の `height` は必要に応じて詰めてよい。

---

## カスタマイズ

### 新しいシリーズを追加

`lib/series_config.py` の `SERIES_CONFIG` 辞書に新エントリを追加：

```python
"new-series-id": {
    "order": 10,                       # 表示順
    "display_name": "新シリーズ名",
    "concept": "1-2行のシリーズ説明",
    "lang": "jp",                       # 'jp' or 'en'
    "cover_class": "device",            # CSSクラス（既存：lncrna/device/ai/science/career/health/en）
},
```

そして `books/<slug>.md` の `series_id:` を `new-series-id` に設定 → 自動表示。

### 表紙画像

`marketing/covers/<slug>/kindle.jpg` が真実源。ジェネレータが自動で `docs/covers/<slug>.jpg` にコピーします。
カバーがない書籍はグラデーションカードでフォールバック表示。

新規カバーは `/kindle-cover` で生成 → 次回 `/kindle-update-hp` で自動同期。

### ペーパーバック版バッジを付ける

`lib/series_config.py` の `PAPERBACK_MAP` に Kindle ASIN → Paperback ASIN を追加：

```python
PAPERBACK_MAP = {
    "B0GZJF83SV": "B0XXXXXXXX",   # 心の中の評議会 → Paperback ASIN
    ...
}
```

将来的には `books/<slug>.md` の YAML に `paperback_asin:` フィールドを足して
ジェネレータ側で読むよう拡張するのが望ましい（todo）。

---

## トラブルシュート

| 症状 | 対処 |
|---|---|
| `/kindle-update-hp` でcommit対象なし | books/*.md に変更がない。Amazon情報を最新化したい場合は `--fetch` を付ける |
| GitHub Pages が404 | Settings → Pages で Source/Folder 設定を再確認。`/docs` 必須 |
| Wix iframe が空白 | `https://<USER>.github.io/hp_books_site/` を直接ブラウザで開いて確認。CORS/HTTPS問題ではない（GitHub Pages はHTTPS） |
| 表紙画像が出ない | `docs/covers/<slug>.jpg` のファイル名が slug と一致しているか確認（`covers/<slug>/kindle.jpg` から自動同期） |
| 英語ページが 404 | URLは `…github.io/hp_books_site/en.html`。GitHub Pages 反映に1〜2分。ユーザー名は `hidenori-tani`（ハイフン有） |
| 冊数が日英でズレる | シリーズ未登録（`series_id` 空）の本は非表示。`series_config.py` に登録済みか確認 |
| iframe の高さが足りない | iframe の `height` を増やす（書籍数増加に応じて） |

---

## なぜこの構成か

- **Wix側を最小限しか触らない**: HTML埋め込み1個。それ以外のページは不可触
- **データは1ヶ所**: `marketing/books/*.md` が真実。Amazon情報も含めて一元管理
- **既存ツールと連携**: `/kindle-fetch` で取得した最新情報がそのまま反映される
- **無料**: GitHub Pages、Google Fonts、すべて無料
- **学習コストゼロ**: 普段は `/kindle-update-hp` だけ覚えればいい

---

## 関連

- `outreach-books/marketing/` — 書籍メタデータの真実源（独立 git repo）
- `outreach-books/marketing/CLAUDE.md` — Kindle マーケティング自動化サブプロジェクトAの全体仕様
- `/kindle-fetch`, `/kindle-optimize` — メタデータ更新・最適化用既存スキル
