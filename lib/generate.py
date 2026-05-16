#!/usr/bin/env python3
"""
hidenoritani.com 著書ページ HTML ジェネレータ

入力: ../marketing/books/*.md (YAML frontmatter)
出力: ../docs/index.html

使い方:
    python3 lib/generate.py

GitHub Pages にデプロイ後、Wix HTML iframe ウィジェットから読み込まれる。
"""

import glob
import html
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from series_config import SERIES_CONFIG, STANDALONE_SECTION, PAPERBACK_MAP

# パス
SCRIPT_DIR = Path(__file__).parent
SITE_ROOT = SCRIPT_DIR.parent
BOOKS_DIR = SITE_ROOT.parent / "marketing" / "books"
OUTPUT_PATH = SITE_ROOT / "docs" / "index.html"
COVERS_DIR = SITE_ROOT / "docs" / "covers"

# 「新刊」判定: pub_date が今日から3ヶ月以内
NEW_THRESHOLD = datetime.now() - timedelta(days=90)


def load_books():
    """books/*.md を読み込み、販売中のみ返す"""
    books = []
    for md_path in sorted(glob.glob(str(BOOKS_DIR / "*.md"))):
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        if not content.startswith("---"):
            continue
        fm_end = content.find("---", 3)
        if fm_end < 0:
            continue
        try:
            fm = yaml.safe_load(content[3:fm_end])
        except yaml.YAMLError as e:
            print(f"WARN: YAML parse failed for {md_path}: {e}", file=sys.stderr)
            continue
        if not fm:
            continue
        if fm.get("unpublished"):
            continue
        if not fm.get("asin"):
            continue
        books.append(fm)
    return books


def is_new(pub_date_str):
    if not pub_date_str:
        return False
    try:
        # YAML may parse as date or string
        if isinstance(pub_date_str, str):
            d = datetime.strptime(pub_date_str[:10], "%Y-%m-%d")
        else:
            d = datetime.combine(pub_date_str, datetime.min.time())
        return d >= NEW_THRESHOLD
    except (ValueError, TypeError):
        return False


def cover_url_or_none(asin):
    """docs/covers/<ASIN>.jpg があればそのパスを返す"""
    p = COVERS_DIR / f"{asin}.jpg"
    if p.exists():
        return f"covers/{asin}.jpg"
    p = COVERS_DIR / f"{asin}.png"
    if p.exists():
        return f"covers/{asin}.png"
    return None


def amazon_url(asin, lang):
    """ASIN → Amazon URL（lang=jp/en）"""
    domain = "amazon.com" if lang == "en" else "amazon.co.jp"
    return f"https://www.{domain}/dp/{asin}"


def fmt_date(pub_date_str):
    if not pub_date_str:
        return ""
    s = str(pub_date_str)[:10]
    return s.replace("-", ".")


def render_book_card(book, cover_class):
    """1冊分のカードHTML"""
    asin = book.get("asin", "")
    title = book.get("title", "")
    subtitle = book.get("subtitle", "") or ""
    pub_date = book.get("pub_date", "")
    rating = book.get("average_rating")
    review_count = book.get("review_count", 0)

    # シリーズ情報から言語判定
    sid = book.get("series_id")
    lang = "en"
    if sid and sid in SERIES_CONFIG:
        lang = SERIES_CONFIG[sid]["lang"]
    elif sid is None:
        # standalone — 英語の可能性が高いがタイトルから判定
        lang = "en" if all(ord(c) < 128 for c in title[:20]) else "jp"

    # カバー画像 or プレースホルダ
    cover_path = cover_url_or_none(asin)
    if cover_path:
        cover_html = f'<div class="cover"><img src="{html.escape(cover_path)}" alt="{html.escape(title)}"></div>'
    else:
        # タイトルを2-3行に折って表示
        display = title.split(":")[0].split("：")[0]
        if len(display) > 16:
            mid = len(display) // 2
            display = display[:mid] + "<br>" + display[mid:]
        cover_html = f'<div class="cover {cover_class}">{display}</div>'

    # バッジ
    badges = []
    if is_new(pub_date):
        badges.append('<span class="badge new">' + ("NEW" if lang == "en" else "新刊") + "</span>")
    if asin in PAPERBACK_MAP:
        badges.append('<span class="badge paperback">📖 ' + ("Paperback" if lang == "en" else "紙版") + "</span>")
    if rating and review_count and review_count >= 1:
        try:
            r = float(rating)
            if r >= 4.0:
                badges.append(f'<span class="badge review">★{r:.1f}</span>')
        except (ValueError, TypeError):
            pass
    badges_html = ""
    if badges:
        badges_html = '<div class="badges">' + "".join(badges) + "</div>"

    # メタ
    meta_parts = []
    if pub_date:
        meta_parts.append(fmt_date(pub_date))
    if lang == "en":
        meta_parts.append("English")
    meta_html = " · ".join(meta_parts)

    # アクション
    btn_label_kindle = "Amazon (US)" if lang == "en" else "Kindleで読む"
    btn_label_pb = "Paperback" if lang == "en" else "ペーパーバック"
    actions = [f'<a class="btn primary" href="{amazon_url(asin, lang)}" target="_blank" rel="noopener">{btn_label_kindle}</a>']
    pb_asin = PAPERBACK_MAP.get(asin)
    if pb_asin:
        actions.append(f'<a class="btn" href="{amazon_url(pb_asin, lang)}" target="_blank" rel="noopener">{btn_label_pb}</a>')

    # サブタイトルが長すぎる場合の処理
    subtitle_html = f'<p class="book-subtitle">{html.escape(subtitle)}</p>' if subtitle else ""

    return f"""
      <article class="book-card">
        {cover_html}
        {badges_html}
        <h3 class="book-title">{html.escape(title.split(':')[0].split('：')[0])}</h3>
        {subtitle_html}
        <div class="book-meta">{html.escape(meta_html)}</div>
        <div class="book-actions">
          {''.join(actions)}
        </div>
      </article>"""


def render_series_section(series_id, books, config, section_num):
    """1シリーズ分のセクションHTML"""
    n = len(books)
    grid_class = "books-grid"
    if n == 2:
        grid_class += " cols-2"
    elif n == 1:
        grid_class += " cols-1"

    # 新→古
    sorted_books = sorted(books, key=lambda b: str(b.get("pub_date", "")), reverse=True)
    cards = "\n".join(render_book_card(b, config["cover_class"]) for b in sorted_books)

    return f"""
<section class="series-section" id="s{section_num}">
  <div class="wrap">
    <div class="series-header">
      <div class="series-num">SERIES {section_num:02d}</div>
      <h2 class="series-title">{html.escape(config["display_name"])}</h2>
      <p class="series-concept">{html.escape(config["concept"])}</p>
    </div>
    <div class="{grid_class}">
      {cards}
    </div>
  </div>
</section>"""


def render_new_releases(books):
    """新刊3冊（最新の出版日順）"""
    new_books = sorted(
        [b for b in books if is_new(b.get("pub_date"))],
        key=lambda b: str(b.get("pub_date", "")),
        reverse=True,
    )[:3]
    if not new_books:
        return ""
    cards = "\n".join(
        render_book_card(b, SERIES_CONFIG.get(b.get("series_id"), {"cover_class": "device"})["cover_class"])
        for b in new_books
    )
    return f"""
<section class="new-releases">
  <div class="wrap">
    <div class="section-label">NEW RELEASES</div>
    <h2 class="section-title">🆕 新刊</h2>
    <div class="new-grid">
      {cards}
    </div>
  </div>
</section>"""


def render_nav(series_groups):
    """シリーズナビゲーション"""
    items = []
    section_num = 1
    for sid, books in series_groups:
        if sid is None:
            continue
        config = SERIES_CONFIG.get(sid)
        if not config:
            continue
        name = config["display_name"]
        items.append(
            f'<a href="#s{section_num}">{section_num:02d} {html.escape(name)}<span class="count">({len(books)})</span></a>'
        )
        section_num += 1
    return f"""
<nav class="series-nav">
  <div class="series-nav-inner">
    {''.join(items)}
  </div>
</nav>"""


CSS = """
:root {
  --ink: #1a1a1a;
  --ink-soft: #555;
  --paper: #fafaf7;
  --accent: #2c4a6e;
  --accent-soft: #5a7a9e;
  --line: #d8d4cc;
  --new: #b8412e;
  --paperback: #6b5d3f;
}
* { box-sizing: border-box; }
body {
  font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif;
  color: var(--ink);
  background: var(--paper);
  margin: 0;
  line-height: 1.7;
  font-size: 16px;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 24px; }

.hero {
  text-align: center;
  padding: 70px 24px 50px;
  border-bottom: 1px solid var(--line);
}
.hero h1 { font-size: 38px; margin: 0 0 6px; letter-spacing: 0.05em; font-weight: 500; }
.hero .sub-en {
  font-family: "Garamond", "EB Garamond", serif;
  font-size: 16px; color: var(--ink-soft);
  letter-spacing: 0.2em; margin-bottom: 22px;
}
.hero .lead { max-width: 640px; margin: 0 auto 28px; color: var(--ink-soft); font-size: 16px; }
.cta-row { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.cta {
  display: inline-block; padding: 11px 24px;
  background: var(--accent); color: #fff; text-decoration: none;
  font-size: 13px; letter-spacing: 0.08em;
  border: 1px solid var(--accent); transition: background 0.2s;
}
.cta:hover { background: var(--accent-soft); }
.cta.outline { background: transparent; color: var(--accent); }
.cta.outline:hover { background: var(--accent); color: #fff; }

.new-releases {
  padding: 50px 0 30px;
  background: #fff;
  border-bottom: 1px solid var(--line);
}
.section-label { text-align: center; font-size: 12px; letter-spacing: 0.3em; color: var(--ink-soft); margin-bottom: 6px; }
.section-title { text-align: center; font-size: 24px; margin: 0 0 32px; font-weight: 500; letter-spacing: 0.05em; }
.new-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }

.series-nav {
  padding: 28px 24px;
  background: var(--paper);
  border-bottom: 1px solid var(--line);
  text-align: center;
}
.series-nav-inner {
  display: flex; flex-wrap: wrap;
  justify-content: center; gap: 8px 22px;
  max-width: 900px; margin: 0 auto;
}
.series-nav a {
  color: var(--accent); text-decoration: none;
  font-size: 13px; padding: 4px 0;
  border-bottom: 1px solid transparent; transition: border-color 0.2s;
}
.series-nav a:hover { border-color: var(--accent); }
.series-nav .count { color: var(--ink-soft); font-size: 11px; margin-left: 4px; }

.series-section { padding: 60px 0 30px; border-bottom: 1px solid var(--line); }
.series-section:last-of-type { border-bottom: none; }
.series-header { text-align: center; margin-bottom: 32px; }
.series-num {
  display: inline-block; font-family: "Garamond", serif;
  font-size: 13px; letter-spacing: 0.3em;
  color: var(--accent); margin-bottom: 6px;
}
.series-title { font-size: 24px; margin: 0 0 10px; font-weight: 500; }
.series-concept { color: var(--ink-soft); max-width: 600px; margin: 0 auto; font-size: 14px; }

.books-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 24px; }
.books-grid.cols-2 { grid-template-columns: repeat(2, 1fr); max-width: 700px; margin-left: auto; margin-right: auto; }
.books-grid.cols-1 { grid-template-columns: 1fr; max-width: 340px; margin-left: auto; margin-right: auto; }

.book-card {
  background: #fff; border: 1px solid var(--line);
  padding: 20px; display: flex; flex-direction: column;
  transition: box-shadow 0.2s, transform 0.2s;
}
.book-card:hover {
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.cover {
  aspect-ratio: 2 / 3;
  background: linear-gradient(135deg, #e8e1d4 0%, #c9bfa9 100%);
  margin-bottom: 14px;
  display: flex; align-items: center; justify-content: center;
  padding: 14px; text-align: center;
  color: var(--ink); font-size: 13px; line-height: 1.4; font-weight: 500;
  overflow: hidden;
}
.cover img { width: 100%; height: 100%; object-fit: cover; }
.cover.lncrna  { background: linear-gradient(135deg, #d4e1e8 0%, #95b3c4 100%); }
.cover.device  { background: linear-gradient(135deg, #2c4a6e 0%, #5a7a9e 100%); color: #fff; }
.cover.ai      { background: linear-gradient(135deg, #f0e8d4 0%, #c9b888 100%); }
.cover.science { background: linear-gradient(135deg, #e8d4d4 0%, #b89595 100%); }
.cover.career  { background: linear-gradient(135deg, #d4e8d4 0%, #95b895 100%); }
.cover.health  { background: linear-gradient(135deg, #f0d4e1 0%, #c995b3 100%); }
.cover.en      { background: linear-gradient(135deg, #1a1a1a 0%, #555 100%); color: #fff; font-family: "Garamond", serif; letter-spacing: 0.05em; }

.badges { display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }
.badge { font-size: 10px; padding: 2px 7px; border-radius: 2px; letter-spacing: 0.05em; }
.badge.new { background: var(--new); color: #fff; }
.badge.paperback { background: var(--paperback); color: #fff; }
.badge.review { background: #d4a000; color: #fff; }

.book-title { font-size: 15px; line-height: 1.5; margin: 0 0 6px; font-weight: 500; }
.book-subtitle { font-size: 12px; color: var(--ink-soft); margin: 0 0 10px; line-height: 1.5; }
.book-meta { font-size: 11px; color: var(--ink-soft); margin-bottom: 14px; margin-top: auto; }
.book-actions { display: flex; flex-direction: column; gap: 5px; }
.btn {
  display: block; text-align: center;
  padding: 7px 10px; text-decoration: none; font-size: 12px;
  border: 1px solid var(--accent); color: var(--accent); transition: all 0.2s;
}
.btn:hover { background: var(--accent); color: #fff; }
.btn.primary { background: var(--accent); color: #fff; }
.btn.primary:hover { background: var(--accent-soft); border-color: var(--accent-soft); }

.footer-cta { padding: 70px 24px; background: #fff; text-align: center; border-top: 1px solid var(--line); }
.footer-cta h2 { font-size: 22px; margin: 0 0 14px; font-weight: 500; }
.footer-cta p { color: var(--ink-soft); margin-bottom: 28px; }
.footer-meta { padding: 20px; text-align: center; font-size: 11px; color: var(--ink-soft); }

@media (max-width: 720px) {
  .hero h1 { font-size: 28px; }
  .new-grid, .books-grid, .books-grid.cols-2 { grid-template-columns: 1fr; max-width: 340px; margin-left: auto; margin-right: auto; }
  .series-section { padding: 40px 0 20px; }
}
"""


def render_html(books):
    """全体HTML"""
    # シリーズ別グループ化
    by_series = {}
    standalone = []
    for b in books:
        sid = b.get("series_id")
        if sid is None:
            standalone.append(b)
        else:
            by_series.setdefault(sid, []).append(b)

    # 表示順ソート
    series_groups = []
    for sid in sorted(by_series.keys(), key=lambda s: SERIES_CONFIG.get(s, {"order": 999})["order"]):
        if sid in SERIES_CONFIG:
            series_groups.append((sid, by_series[sid]))

    # standalone を末尾に
    if standalone:
        series_groups.append((None, standalone))

    # 各セクションを描画
    sections_html = []
    section_num = 1
    for sid, slist in series_groups:
        if sid is None:
            config = STANDALONE_SECTION
        else:
            config = SERIES_CONFIG[sid]
        sections_html.append(render_series_section(sid or "standalone", slist, config, section_num))
        section_num += 1

    new_releases_html = render_new_releases(books)
    nav_html = render_nav(series_groups)

    total = len(books)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>著書 / Books — 谷英典</title>
<meta name="description" content="谷英典（横浜薬科大学准教授）の著書一覧。lncRNA研究、AI時代の研究者の働き方、装置運用世代シリーズなど{total}冊。">
<style>{CSS}</style>
</head>
<body>

<section class="hero">
  <div class="wrap">
    <h1>著書</h1>
    <div class="sub-en">BOOKS</div>
    <p class="lead">
      ライフサイエンス研究（lncRNA・RNA創薬）から、AI時代に研究者が生き残る技法まで——<br>
      現在 {total} 冊を執筆しています。
    </p>
    <div class="cta-row">
      <a class="cta" href="https://www.amazon.co.jp/stores/author/B0DBNS3FZF" target="_blank" rel="noopener">
        Amazon Author Central（日本語）
      </a>
      <a class="cta outline" href="https://www.amazon.com/author/hidenoritani" target="_blank" rel="noopener">
        Author Central (English)
      </a>
    </div>
  </div>
</section>

{new_releases_html}

{nav_html}

{''.join(sections_html)}

<section class="footer-cta">
  <div class="wrap">
    <h2>すべての著作を一覧で見る</h2>
    <p>Amazon Author Central では、ペーパーバック版を含む全著作・新刊情報・著者プロフィールをご覧いただけます。</p>
    <div class="cta-row">
      <a class="cta" href="https://www.amazon.co.jp/stores/author/B0DBNS3FZF" target="_blank" rel="noopener">
        日本語：amazon.co.jp
      </a>
      <a class="cta outline" href="https://www.amazon.com/author/hidenoritani" target="_blank" rel="noopener">
        English: amazon.com
      </a>
    </div>
  </div>
</section>

<div class="footer-meta">Last updated: {generated}</div>

</body>
</html>
"""


def main():
    books = load_books()
    print(f"Loaded {len(books)} published books from {BOOKS_DIR}")
    html_out = render_html(books)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Wrote {OUTPUT_PATH} ({len(html_out):,} bytes)")


if __name__ == "__main__":
    main()
