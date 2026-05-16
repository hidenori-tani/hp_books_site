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
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from series_config import SERIES_CONFIG, STANDALONE_SECTION, PAPERBACK_MAP

# パス
SCRIPT_DIR = Path(__file__).parent
SITE_ROOT = SCRIPT_DIR.parent
BOOKS_DIR = SITE_ROOT.parent / "marketing" / "books"
SOURCE_COVERS_DIR = SITE_ROOT.parent / "marketing" / "covers"
OUTPUT_PATH = SITE_ROOT / "docs" / "index.html"
COVERS_DIR = SITE_ROOT / "docs" / "covers"

# 「新刊」判定: pub_date が今日から3ヶ月以内
NEW_THRESHOLD = datetime.now() - timedelta(days=90)

# 日本語のみ表示（英語シリーズと standalone は除外）
EXCLUDE_LANG = "en"


def load_books():
    """books/*.md を読み込み、販売中の日本語書籍のみ返す"""
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
        # 英語シリーズ・standalone を除外
        sid = fm.get("series_id")
        if sid is None:
            continue  # standalone は英語のみなのでスキップ
        config = SERIES_CONFIG.get(sid)
        if config and config.get("lang") == EXCLUDE_LANG:
            continue
        books.append(fm)
    return books


def sync_covers(books):
    """marketing/covers/<slug>/kindle.jpg を docs/covers/<slug>.jpg にコピー"""
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for book in books:
        slug = book.get("slug")
        if not slug:
            continue
        src = SOURCE_COVERS_DIR / slug / "kindle.jpg"
        if not src.exists():
            continue
        dst = COVERS_DIR / f"{slug}.jpg"
        # mtime チェックで不要なコピーを回避
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        shutil.copy2(src, dst)
        copied += 1
    return copied


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


def cover_url_or_none(slug):
    """docs/covers/<slug>.jpg があればそのパスを返す"""
    if not slug:
        return None
    p = COVERS_DIR / f"{slug}.jpg"
    if p.exists():
        return f"covers/{slug}.jpg"
    p = COVERS_DIR / f"{slug}.png"
    if p.exists():
        return f"covers/{slug}.png"
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
    slug = book.get("slug")
    cover_path = cover_url_or_none(slug)
    if cover_path:
        cover_html = f'<div class="cover has-image"><img src="{html.escape(cover_path)}" alt="{html.escape(title)}"></div>'
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
/* Match hidenoritani.com (Wix) palette:
   Headings: Playfair Display, Body: Raleway, Italic accent: Playfair Italic
   Accent: #0057E1 (Wix color_18), ink: #000, paper: #fff */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=Raleway:wght@300;400;500;600&display=swap');

:root {
  --ink: #000;
  --ink-soft: #4d4d4d;
  --ink-mute: #888;
  --paper: #fff;
  --accent: #0057E1;
  --accent-soft: #4a85ea;
  --line: #e8e6e6;
  --new: #c0392b;
  --paperback: #7a6a4a;
}
* { box-sizing: border-box; }
body {
  font-family: 'Raleway', "Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif;
  color: var(--ink);
  background: var(--paper);
  margin: 0;
  line-height: 1.79;
  font-size: 15px;
  font-weight: 400;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 24px; }

h1, h2, h3 { font-family: 'Playfair Display', "Hiragino Mincho ProN", "Yu Mincho", serif; font-weight: 400; }

.hero {
  text-align: center;
  padding: 80px 24px 60px;
  border-bottom: 1px solid var(--line);
  background: var(--paper);
}
.hero h1 {
  font-size: 50px;
  margin: 0 0 8px;
  line-height: 1.34;
  letter-spacing: 0.01em;
}
.hero .sub-en {
  font-family: 'Playfair Display', serif;
  font-style: italic;
  font-size: 20px;
  color: var(--ink-soft);
  letter-spacing: 0.08em;
  margin-bottom: 28px;
}
.hero .lead {
  max-width: 640px;
  margin: 0 auto 32px;
  color: var(--ink-soft);
  font-size: 15px;
  line-height: 1.875;
}
.cta-row { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.cta {
  display: inline-block;
  padding: 12px 28px;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  font-family: 'Raleway', sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.08em;
  border: 1px solid var(--accent);
  transition: background 0.2s;
}
.cta:hover { background: var(--accent-soft); border-color: var(--accent-soft); }
.cta.outline { background: transparent; color: var(--accent); }
.cta.outline:hover { background: var(--accent); color: #fff; }

.new-releases {
  padding: 60px 0 40px;
  background: var(--paper);
  border-bottom: 1px solid var(--line);
}
.section-label {
  text-align: center;
  font-family: 'Raleway', sans-serif;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.3em;
  color: var(--ink-mute);
  margin-bottom: 8px;
}
.section-title {
  text-align: center;
  font-size: 28px;
  margin: 0 0 36px;
  letter-spacing: 0.02em;
}
.new-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }

.series-nav {
  padding: 32px 24px;
  background: var(--paper);
  border-bottom: 1px solid var(--line);
  text-align: center;
}
.series-nav-inner {
  display: flex; flex-wrap: wrap;
  justify-content: center; gap: 8px 26px;
  max-width: 920px; margin: 0 auto;
}
.series-nav a {
  font-family: 'Raleway', sans-serif;
  color: var(--accent); text-decoration: none;
  font-size: 13px; padding: 4px 0;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}
.series-nav a:hover { border-color: var(--accent); }
.series-nav .count { color: var(--ink-mute); font-size: 11px; margin-left: 4px; }

.series-section { padding: 70px 0 40px; border-bottom: 1px solid var(--line); }
.series-section:last-of-type { border-bottom: none; }
.series-header { text-align: center; margin-bottom: 36px; }
.series-num {
  display: inline-block;
  font-family: 'Playfair Display', serif;
  font-style: italic;
  font-size: 14px;
  letter-spacing: 0.15em;
  color: var(--accent);
  margin-bottom: 8px;
}
.series-title { font-size: 28px; margin: 0 0 12px; letter-spacing: 0.01em; }
.series-concept {
  color: var(--ink-soft);
  max-width: 620px;
  margin: 0 auto;
  font-size: 14px;
  line-height: 1.79;
}

.books-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin-top: 28px; }
.books-grid.cols-2 { grid-template-columns: repeat(2, 1fr); max-width: 720px; margin-left: auto; margin-right: auto; }
.books-grid.cols-1 { grid-template-columns: 1fr; max-width: 360px; margin-left: auto; margin-right: auto; }

.book-card {
  background: #fff;
  border: 1px solid var(--line);
  padding: 22px;
  display: flex; flex-direction: column;
  transition: box-shadow 0.25s, transform 0.25s;
}
.book-card:hover {
  box-shadow: 0 10px 28px rgba(0,0,0,0.07);
  transform: translateY(-3px);
}
.cover {
  aspect-ratio: 2 / 3;
  background: linear-gradient(135deg, #e8e6e6 0%, #c4c4c4 100%);
  margin-bottom: 16px;
  display: flex; align-items: center; justify-content: center;
  padding: 16px; text-align: center;
  color: var(--ink); font-size: 13px; line-height: 1.5;
  font-family: 'Playfair Display', "Hiragino Mincho ProN", serif;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.cover.has-image {
  background: #fff;
  padding: 0;
}
.cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cover.lncrna  { background: linear-gradient(135deg, #dce6ec 0%, #8ba8b8 100%); color: #1a1a1a; }
.cover.device  { background: linear-gradient(135deg, #1a3050 0%, #4a6890 100%); color: #fff; }
.cover.ai      { background: linear-gradient(135deg, #f0eadc 0%, #c4b288 100%); color: #1a1a1a; }
.cover.science { background: linear-gradient(135deg, #e8dcdc 0%, #b08888 100%); color: #1a1a1a; }
.cover.career  { background: linear-gradient(135deg, #dce8dc 0%, #8bb08b 100%); color: #1a1a1a; }
.cover.health  { background: linear-gradient(135deg, #f0dce6 0%, #c488a8 100%); color: #1a1a1a; }
.cover.en      { background: linear-gradient(135deg, #080808 0%, #4d4d4d 100%); color: #fff; font-style: italic; letter-spacing: 0.03em; }

.badges { display: flex; gap: 5px; margin-bottom: 8px; flex-wrap: wrap; }
.badge {
  font-family: 'Raleway', sans-serif;
  font-size: 10px; padding: 2px 7px;
  letter-spacing: 0.08em; font-weight: 500;
}
.badge.new { background: var(--new); color: #fff; }
.badge.paperback { background: var(--paperback); color: #fff; }
.badge.review { background: #c89a00; color: #fff; }

.book-title {
  font-family: 'Playfair Display', "Hiragino Mincho ProN", "Yu Mincho", serif;
  font-size: 16px; line-height: 1.5;
  margin: 0 0 6px; font-weight: 500;
}
.book-subtitle {
  font-family: 'Raleway', sans-serif;
  font-size: 12px; color: var(--ink-soft);
  margin: 0 0 10px; line-height: 1.6;
}
.book-meta {
  font-family: 'Raleway', sans-serif;
  font-size: 11px; color: var(--ink-mute);
  margin-bottom: 14px; margin-top: auto;
  letter-spacing: 0.04em;
}
.book-actions { display: flex; flex-direction: column; gap: 6px; }
.btn {
  display: block; text-align: center;
  padding: 8px 12px; text-decoration: none;
  font-family: 'Raleway', sans-serif;
  font-size: 12px; font-weight: 500;
  letter-spacing: 0.05em;
  border: 1px solid var(--accent); color: var(--accent);
  transition: all 0.2s;
}
.btn:hover { background: var(--accent); color: #fff; }
.btn.primary { background: var(--accent); color: #fff; }
.btn.primary:hover { background: var(--accent-soft); border-color: var(--accent-soft); }

.footer-cta {
  padding: 80px 24px;
  background: var(--paper);
  text-align: center;
  border-top: 1px solid var(--line);
}
.footer-cta h2 { font-size: 24px; margin: 0 0 14px; letter-spacing: 0.01em; }
.footer-cta p { color: var(--ink-soft); margin-bottom: 32px; font-size: 14px; }
.footer-meta {
  padding: 20px;
  text-align: center;
  font-family: 'Raleway', sans-serif;
  font-size: 11px;
  color: var(--ink-mute);
  letter-spacing: 0.05em;
}

@media (max-width: 720px) {
  .hero { padding: 60px 24px 40px; }
  .hero h1 { font-size: 36px; }
  .hero .sub-en { font-size: 16px; }
  .new-grid, .books-grid, .books-grid.cols-2 { grid-template-columns: 1fr; max-width: 360px; margin-left: auto; margin-right: auto; }
  .series-section { padding: 50px 0 30px; }
  .section-title, .series-title { font-size: 22px; }
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
    print(f"Loaded {len(books)} Japanese published books from {BOOKS_DIR}")
    copied = sync_covers(books)
    print(f"Synced {copied} cover image(s) to {COVERS_DIR}")
    html_out = render_html(books)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Wrote {OUTPUT_PATH} ({len(html_out):,} bytes)")


if __name__ == "__main__":
    main()
