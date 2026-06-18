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
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

from series_config import SERIES_CONFIG

# パス
SCRIPT_DIR = Path(__file__).parent
SITE_ROOT = SCRIPT_DIR.parent
BOOKS_DIR = SITE_ROOT.parent / "books"
SOURCE_COVERS_DIR = SITE_ROOT.parent / "covers"
OUTPUT_PATH = SITE_ROOT / "docs" / "index.html"
COVERS_DIR = SITE_ROOT / "docs" / "covers"

# 日本語・英語両方のシリーズを表示（series_id 未設定の standalone は除外）
# 個別フィルタは load_books() 内で処理


def load_books():
    """books/*.md を読み込み、販売中の書籍（日本語＋英語シリーズ）を返す"""
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
        # series_id 未設定の standalone は除外
        sid = fm.get("series_id")
        if sid is None:
            continue
        config = SERIES_CONFIG.get(sid)
        if not config:
            continue  # 未登録 series_id は除外
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


def _render_series_card(config, books, section_num):
    """1シリーズのカードを生成"""
    sorted_books = sorted(books, key=lambda b: str(b.get("pub_date", "")), reverse=True)
    thumbs = []
    for b in sorted_books:
        cp = cover_url_or_none(b.get("slug"))
        asin = b.get("asin", "")
        title = b.get("title", "")
        url = amazon_url(asin, config.get("lang", "jp"))
        if cp:
            thumbs.append(
                f'<a href="{url}" target="_blank" rel="noopener" title="{html.escape(title)}">'
                f'<img src="{html.escape(cp)}" alt="{html.escape(title)}"></a>'
            )
        else:
            short = title.split(":")[0].split("：")[0][:20]
            thumbs.append(
                f'<a href="{url}" target="_blank" rel="noopener" title="{html.escape(title)}" class="thumb-text">'
                f'<span>{html.escape(short)}</span></a>'
            )
    thumb_count_class = f"thumbs-{min(len(thumbs), 3)}"
    thumbs_html = f'<div class="series-thumbs {thumb_count_class}">{"".join(thumbs)}</div>'
    count_label = f'全{len(books)}冊' if config.get("lang") != "en" else f'{len(books)} {"books" if len(books) != 1 else "book"}'

    return f"""
      <article class="series-overview-card">
        {thumbs_html}
        <div class="series-overview-meta">
          <div class="series-overview-num">SERIES {section_num:02d}</div>
          <h3 class="series-overview-title">{html.escape(config["display_name"])}</h3>
          <p class="series-overview-concept">{html.escape(config["concept"])}</p>
          <div class="series-overview-count">{count_label}</div>
        </div>
      </article>"""


def render_optin():
    """メール登録セクション。SITE_ROOT/optin_embed.html があれば表示、
    無ければ何も出さない（MailerLite未設定の段階で壊れた空フォームを公開しないため）。"""
    embed_path = SITE_ROOT / "optin_embed.html"
    if not embed_path.exists():
        return ""
    embed = embed_path.read_text(encoding="utf-8").strip()
    if not embed:
        return ""
    return f"""
<section class="optin">
  <div class="wrap">
    <div class="section-label">FREE GUIDE</div>
    <h2 class="section-title">RNA創薬の全体像マップを無料で</h2>
    <p class="optin-lead">mRNA・miRNA・siRNA・ASO・アプタマーを「作らせる／抑える／狙う」の一枚に整理したPDF（A4・2ページ）。ご登録の方に、RNAと生命科学のやさしい解説や新刊のお知らせを、ときどきお届けします。</p>
    <div class="optin-form">{embed}</div>
  </div>
</section>"""


OPTIN_CSS = """
.optin { padding: 56px 24px; background: #f5f8ff; border-top: 1px solid #e3e9f5; border-bottom: 1px solid #e3e9f5; }
.optin .section-label { color: #0057E1; }
.optin .optin-lead { max-width: 680px; margin: 14px auto 26px; text-align: center; line-height: 1.85; color: #333; font-size: 16px; }
.optin .optin-form { max-width: 520px; margin: 0 auto; }
.optin .optin-form input[type=email] { width: 100%; padding: 13px 15px; font-size: 16px; border: 1px solid #b9c4dd; border-radius: 8px; }
.optin .optin-form button, .optin .optin-form input[type=submit] { background: #0057E1; color: #fff; border: 0; border-radius: 8px; padding: 13px 22px; font-size: 16px; cursor: pointer; }
@media (max-width: 640px) { .optin { padding: 40px 20px; } }
"""


def review_url(asin, lang):
    """ASIN → Amazon「レビューを書く」URL（lang=jp/en）"""
    domain = "amazon.com" if lang == "en" else "amazon.co.jp"
    return f"https://www.{domain}/review/create-review?asin={asin}"


def render_review_cta(books):
    """読者に正直なレビューをお願いするセクション。
    Amazon規約準拠：特典・星数の限定なし。肯定も率直な意見も歓迎する姿勢で「正直な感想」を求める。
    """
    jp_items, en_items = [], []
    for b in sorted(books, key=lambda x: str(x.get("pub_date", "")), reverse=True):
        asin = b.get("asin", "")
        if not asin:
            continue
        sid = b.get("series_id")
        lang = SERIES_CONFIG.get(sid, {}).get("lang", "jp")
        short = b.get("title", "").split(":")[0].split("：")[0]
        item = (f'<li><a href="{review_url(asin, lang)}" target="_blank" rel="noopener">'
                f'{html.escape(short)}</a></li>')
        (en_items if lang == "en" else jp_items).append(item)

    if not jp_items and not en_items:
        return ""

    blocks = []
    if jp_items:
        blocks.append(
            '<div class="review-col"><h3 class="review-sub">日本語の著作</h3>'
            f'<ul class="review-list">{"".join(jp_items)}</ul></div>'
        )
    if en_items:
        blocks.append(
            '<div class="review-col"><h3 class="review-sub">English titles</h3>'
            f'<ul class="review-list">{"".join(en_items)}</ul></div>'
        )

    return f"""
<section class="review-cta">
  <div class="wrap">
    <div class="section-label">REVIEWS</div>
    <h2 class="section-title">読んでくださった方へ、ひとつだけお願いです</h2>
    <p class="review-lead">どの本でも、お読みいただいた率直なご感想を Amazon にひとことだけ残していただけたら、とても励みになります。「ここが役に立った」も「ここはこう思う」も、どちらも歓迎です。あなたの一言が、これから同じ問いで本を探す次の誰かの道しるべになります。星の数よりも、感じたことそのものが何よりの参考になります。</p>
    <div class="review-cols">{"".join(blocks)}</div>
  </div>
</section>"""


REVIEW_CSS = """
.review-cta { padding: 56px 24px; background: #fbfcff; border-top: 1px solid #e3e9f5; }
.review-cta .section-label { color: #0057E1; }
.review-cta .review-lead { max-width: 720px; margin: 14px auto 30px; text-align: center; line-height: 1.95; color: #333; font-size: 16px; }
.review-cta .review-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; max-width: 920px; margin: 0 auto; }
.review-cta .review-sub { font-size: 15px; color: #0057E1; margin: 0 0 10px; letter-spacing: .04em; }
.review-cta .review-list { list-style: none; padding: 0; margin: 0; columns: 2; column-gap: 22px; }
.review-cta .review-list li { margin: 0 0 8px; break-inside: avoid; font-size: 14px; line-height: 1.5; }
.review-cta .review-list a { color: #1a2b4a; text-decoration: none; border-bottom: 1px solid #c9d6ee; }
.review-cta .review-list a:hover { color: #0057E1; border-bottom-color: #0057E1; }
@media (max-width: 720px) { .review-cta .review-cols { grid-template-columns: 1fr; gap: 20px; } .review-cta .review-list { columns: 1; } }
"""


def render_series_overview(series_groups):
    """全シリーズ一覧（日本語・英語をセクションに分けて表示）"""
    jp_cards = []
    en_cards = []
    section_num = 1
    for sid, books in series_groups:
        if sid is None:
            continue
        config = SERIES_CONFIG.get(sid)
        if not config:
            continue
        card_html = _render_series_card(config, books, section_num)
        if config.get("lang") == "en":
            en_cards.append(card_html)
        else:
            jp_cards.append(card_html)
        section_num += 1

    if not jp_cards and not en_cards:
        return ""

    sections = []
    if jp_cards:
        sections.append(f"""
<section class="series-overview">
  <div class="wrap">
    <div class="section-label">ALL SERIES</div>
    <h2 class="section-title">シリーズ一覧</h2>
    <p class="series-overview-hint">表紙をクリックすると Amazon のページが開きます</p>
    <div class="series-overview-grid">
      {''.join(jp_cards)}
    </div>
  </div>
</section>""")

    if en_cards:
        sections.append(f"""
<section class="series-overview">
  <div class="wrap">
    <div class="section-label">ENGLISH EDITIONS</div>
    <h2 class="section-title">English Books</h2>
    <p class="series-overview-hint">Click a cover to open the Amazon.com page.</p>
    <div class="series-overview-grid">
      {''.join(en_cards)}
    </div>
  </div>
</section>""")

    return "\n".join(sections)


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

.series-overview {
  padding: 60px 0 50px;
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
.series-overview-hint {
  text-align: center;
  font-family: 'Raleway', sans-serif;
  font-size: 12px;
  color: var(--ink-mute);
  margin: 0 0 28px;
  letter-spacing: 0.05em;
}
.series-overview-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  max-width: 900px;
  margin: 0 auto;
}
.series-overview-card {
  background: #fff;
  border: 1px solid var(--line);
  padding: 28px;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 28px;
  align-items: center;
  transition: box-shadow 0.25s, border-color 0.25s;
}
.series-overview-card:hover {
  box-shadow: 0 10px 28px rgba(0,0,0,0.07);
  border-color: var(--accent);
}
.series-thumbs {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: flex-end;
}
.series-thumbs a {
  flex: 1;
  display: block;
  text-decoration: none;
  transition: transform 0.2s;
}
.series-thumbs a:hover {
  transform: translateY(-4px);
}
.series-thumbs img {
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  box-shadow: 0 3px 10px rgba(0,0,0,0.15);
  display: block;
}
.series-thumbs.thumbs-1 { max-width: 50%; margin: 0 auto; }
.series-thumbs.thumbs-2 { max-width: 70%; margin: 0 auto; }
.thumb-text {
  width: 100%;
  aspect-ratio: 2 / 3;
  background: linear-gradient(135deg, #e8e6e6 0%, #c4c4c4 100%);
  display: flex; align-items: center; justify-content: center;
  padding: 12px; text-align: center;
  color: var(--ink); font-size: 12px;
  font-family: 'Playfair Display', "Hiragino Mincho ProN", serif;
  box-shadow: 0 3px 10px rgba(0,0,0,0.15);
}
.series-overview-meta {
  display: flex;
  flex-direction: column;
}
.series-overview-num {
  font-family: 'Playfair Display', serif;
  font-style: italic;
  font-size: 13px;
  letter-spacing: 0.15em;
  color: var(--accent);
  margin-bottom: 8px;
}
.series-overview-title {
  font-family: 'Playfair Display', "Hiragino Mincho ProN", "Yu Mincho", serif;
  font-size: 22px;
  margin: 0 0 12px;
  font-weight: 500;
  line-height: 1.35;
}
.series-overview-concept {
  font-family: 'Raleway', sans-serif;
  font-size: 14px;
  color: var(--ink-soft);
  line-height: 1.75;
  margin: 0 0 16px;
}
.series-overview-count {
  font-family: 'Raleway', sans-serif;
  font-size: 12px;
  color: var(--ink-mute);
  letter-spacing: 0.1em;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}

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
  .series-overview-card { grid-template-columns: 1fr; gap: 20px; padding: 22px; }
  .series-thumbs { max-width: 70%; margin: 0 auto; }
  .section-title { font-size: 22px; }
  .series-overview-title { font-size: 18px; }
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

    series_overview_html = render_series_overview(series_groups)
    optin_html = render_optin()
    review_cta_html = render_review_cta(books)
    total = len(books)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>著書 / Books — 谷英典</title>
<meta name="description" content="谷英典（横浜薬科大学准教授）の著書一覧。lncRNA研究、AI時代の研究者の働き方、装置運用世代シリーズなど{total}冊。">
<style>{CSS}
{OPTIN_CSS}
{REVIEW_CSS}</style>
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
      <a class="cta" href="https://www.amazon.co.jp/stores/%E8%B0%B7%E8%8B%B1%E5%85%B8/author/B0DC528BF8" target="_blank" rel="noopener">
        Amazon著者ページを見る（日本語）
      </a>
      <a class="cta outline" href="https://www.amazon.com/stores/%E8%B0%B7%E8%8B%B1%E5%85%B8/author/B0DC528BF8" target="_blank" rel="noopener">
        View Amazon Author Page (English)
      </a>
    </div>
  </div>
</section>
{optin_html}
{series_overview_html}
{review_cta_html}

<section class="footer-cta">
  <div class="wrap">
    <h2>すべての著作を一覧で見る</h2>
    <p>Amazonの著者検索ページから、ペーパーバック版を含む全著作をご覧いただけます。</p>
    <div class="cta-row">
      <a class="cta" href="https://www.amazon.co.jp/stores/%E8%B0%B7%E8%8B%B1%E5%85%B8/author/B0DC528BF8" target="_blank" rel="noopener">
        日本語：amazon.co.jp 著者ページ
      </a>
      <a class="cta outline" href="https://www.amazon.com/stores/%E8%B0%B7%E8%8B%B1%E5%85%B8/author/B0DC528BF8" target="_blank" rel="noopener">
        English: amazon.com Author Page
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
    copied = sync_covers(books)
    print(f"Synced {copied} cover image(s) to {COVERS_DIR}")
    html_out = render_html(books)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Wrote {OUTPUT_PATH} ({len(html_out):,} bytes)")


if __name__ == "__main__":
    main()
