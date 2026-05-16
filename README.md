# hp_books_site — hidenoritani.com 著書ページ自動生成

`outreach-books/marketing/books/*.md` の 日本語15冊メタデータから、
hidenoritani.com の **著書ページのみ** を自動生成し、Wix の iframe で表示するパイプライン。

**他ページ（ホーム/研究概要/研究業績/経歴/担当科目/連絡先/English）には一切触れない。**

---

## アーキテクチャ

```
[新刊出版] → books/<slug>.md 追加
            ↓
       /kindle-update-hp
            ↓
   ┌──────────────────────────┐
   │ lib/generate.py           │
   │  - books/*.md 読み込み    │
   │  - 9シリーズに分類        │
   │  - docs/index.html 生成   │
   └──────────────────────────┘
            ↓
        git push origin main
            ↓
   ┌──────────────────────────┐
   │ GitHub Pages              │
   │  https://hidenoritani.    │
   │  github.io/hp_books_site/ │
   └──────────────────────────┘
            ↓
   ┌──────────────────────────┐
   │ Wix「著書」ページの       │
   │ HTML iframe ウィジェット  │
   │ （src=上記URL）           │
   └──────────────────────────┘
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
    ├── index.html               # 自動生成（手で編集しない）
    └── covers/                  # （任意）表紙画像 <ASIN>.jpg を置くと自動表示
```

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
| 表紙画像が出ない | `docs/covers/<ASIN>.jpg` のファイル名が ASIN と完全一致しているか確認 |
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
