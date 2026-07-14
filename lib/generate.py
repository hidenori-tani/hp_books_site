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
    """1シリーズ（カテゴリ）のカードを生成。表紙は最大3冊まで表示。"""
    sorted_books = sorted(books, key=lambda b: str(b.get("pub_date", "")), reverse=True)
    display_books = sorted_books[:3]  # ★同カテゴリの表紙は3冊まで（新しい順）
    thumbs = []
    for b in display_books:
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
    total = len(books)
    if config.get("lang") == "en":
        count_label = f'{total} {"books" if total != 1 else "book"}'
        if total > 3:
            count_label += " (showing 3)"
    else:
        count_label = f'全{total}冊'
        if total > 3:
            count_label = f'全{total}冊（新着3冊を表示）'

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


def render_review_cta(books, lang):
    """読者に正直なレビューをお願いするセクション（言語別・当該言語の本のみ）。
    Amazon規約準拠：特典・星数の限定なし。肯定も率直な意見も歓迎する姿勢で「正直な感想」を求める。
    """
    items = []
    for b in sorted(books, key=lambda x: str(x.get("pub_date", "")), reverse=True):
        asin = b.get("asin", "")
        if not asin:
            continue
        sid = b.get("series_id")
        blang = SERIES_CONFIG.get(sid, {}).get("lang", "jp")
        if blang != lang:
            continue
        short = b.get("title", "").split(":")[0].split("：")[0]
        items.append(f'<li><a href="{review_url(asin, lang)}" target="_blank" rel="noopener">'
                     f'{html.escape(short)}</a></li>')

    if not items:
        return ""

    list_html = f'<div class="review-cols single"><div class="review-col"><ul class="review-list">{"".join(items)}</ul></div></div>'

    if lang == "en":
        return f"""
<section class="review-cta">
  <div class="wrap">
    <div class="section-label">REVIEWS</div>
    <h2 class="section-title">One small favor, if I may</h2>
    <p class="review-lead">If any of these books helped you, a short and honest review on Amazon would mean a great deal. What worked for you — and what didn't — both help the next reader searching with the same question. The words you leave matter far more than the number of stars.</p>
    {list_html}
  </div>
</section>"""

    return f"""
<section class="review-cta">
  <div class="wrap">
    <div class="section-label">REVIEWS</div>
    <h2 class="section-title">読んでくださった方へ、ひとつだけお願いです</h2>
    <p class="review-lead">どの本でも、お読みいただいた率直なご感想を Amazon にひとことだけ残していただけたら、とても励みになります。「ここが役に立った」も「ここはこう思う」も、どちらも歓迎です。あなたの一言が、これから同じ問いで本を探す次の誰かの道しるべになります。星の数よりも、感じたことそのものが何よりの参考になります。</p>
    {list_html}
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


def render_series_overview(series_groups, lang):
    """シリーズ一覧（当該言語のみ・1ページ1言語）"""
    cards = []
    section_num = 1
    for sid, books in series_groups:
        if sid is None:
            continue
        config = SERIES_CONFIG.get(sid)
        if not config:
            continue
        if config.get("lang") != lang:
            continue
        cards.append(_render_series_card(config, books, section_num))
        section_num += 1

    if not cards:
        return ""

    if lang == "en":
        label, title, hint = ("ALL SERIES", "Book Series",
                              "Click a cover to open its Amazon.com page.")
    else:
        label, title, hint = ("ALL SERIES", "シリーズ一覧",
                              "表紙をクリックすると Amazon のページが開きます")

    return f"""
<section class="series-overview">
  <div class="wrap">
    <div class="section-label">{label}</div>
    <h2 class="section-title">{title}</h2>
    <p class="series-overview-hint">{hint}</p>
    <div class="series-overview-grid">
      {''.join(cards)}
    </div>
  </div>
</section>"""


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


EXTRA_CSS = """
.lang-nav { display: flex; justify-content: center; gap: 20px; margin-bottom: 24px; font-family: 'Raleway', sans-serif; font-size: 13px; letter-spacing: 0.08em; }
.lang-nav a { color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent; padding-bottom: 2px; transition: border-color 0.2s; }
.lang-nav a:hover { border-color: var(--accent); }
.lang-nav .active { color: var(--ink); border-bottom: 1px solid var(--ink); padding-bottom: 2px; }
.review-cta .review-cols.single { grid-template-columns: 1fr; max-width: 760px; }
"""

AUTHOR_JP = "https://www.amazon.co.jp/stores/%E8%B0%B7%E8%8B%B1%E5%85%B8/author/B0DC528BF8"
AUTHOR_EN = "https://www.amazon.com/stores/%E8%B0%B7%E8%8B%B1%E5%85%B8/author/B0DC528BF8"


def render_page(all_books, lang):
    """1言語ぶんのページHTML（lang='jp' or 'en'）。当該言語のシリーズのみ表示。"""
    # シリーズ別グループ化（standalone は series_id 無しで load 時に除外済み）
    by_series = {}
    for b in all_books:
        sid = b.get("series_id")
        if sid is None:
            continue
        by_series.setdefault(sid, []).append(b)

    series_groups = []
    for sid in sorted(by_series.keys(), key=lambda s: SERIES_CONFIG.get(s, {"order": 999})["order"]):
        if sid in SERIES_CONFIG:
            series_groups.append((sid, by_series[sid]))

    series_overview_html = render_series_overview(series_groups, lang)
    review_cta_html = render_review_cta(all_books, lang)
    total = sum(1 for b in all_books
                if SERIES_CONFIG.get(b.get("series_id"), {}).get("lang") == lang)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    if lang == "en":
        html_lang = "en"
        title = "Books — Hidenori Tani"
        meta_desc = (f"Books by Hidenori Tani (Associate Professor, Yokohama University of "
                     f"Pharmacy): lncRNA research, RNA therapeutics, and thriving as a "
                     f"researcher in the age of AI. {total} English titles.")
        lang_nav = ('<div class="lang-nav"><a href="index.html">日本語</a>'
                    '<span class="active">English</span></div>')
        hero = f"""
<section class="hero">
  <div class="wrap">
    {lang_nav}
    <h1>Books</h1>
    <div class="sub-en">HIDENORI TANI</div>
    <p class="lead">
      From life-science research (lncRNA and RNA therapeutics) to how researchers thrive in the age of AI —<br>
      currently {total} English titles.
    </p>
    <div class="cta-row">
      <a class="cta" href="{AUTHOR_EN}" target="_blank" rel="noopener">
        View Amazon Author Page
      </a>
      <a class="cta outline" href="index.html">日本語の著書ページ</a>
    </div>
  </div>
</section>"""
        optin_html = ""  # 無料ガイドは日本語版のみ
        footer = f"""
<section class="footer-cta">
  <div class="wrap">
    <h2>See every title</h2>
    <p>Browse all books, including paperback editions, on the Amazon author page.</p>
    <div class="cta-row">
      <a class="cta" href="{AUTHOR_EN}" target="_blank" rel="noopener">
        amazon.com Author Page
      </a>
      <a class="cta outline" href="index.html">日本語の著書ページへ</a>
    </div>
  </div>
</section>"""
    else:
        html_lang = "ja"
        title = "著書 / Books — 谷英典"
        meta_desc = (f"谷英典（横浜薬科大学准教授）の著書一覧。lncRNA研究、AI時代の研究者の"
                     f"働き方、装置運用世代シリーズなど日本語{total}冊。英語版は別ページ。")
        lang_nav = ('<div class="lang-nav"><span class="active">日本語</span>'
                    '<a href="en.html">English</a></div>')
        hero = f"""
<section class="hero">
  <div class="wrap">
    {lang_nav}
    <h1>著書</h1>
    <div class="sub-en">BOOKS</div>
    <p class="lead">
      ライフサイエンス研究（lncRNA・RNA創薬）から、AI時代に研究者が生き残る技法まで——<br>
      現在 日本語 {total} 冊を執筆しています。
    </p>
    <div class="cta-row">
      <a class="cta" href="{AUTHOR_JP}" target="_blank" rel="noopener">
        Amazon著者ページを見る（日本語）
      </a>
      <a class="cta outline" href="en.html">English books</a>
    </div>
  </div>
</section>"""
        optin_html = render_optin()
        footer = f"""
<section class="footer-cta">
  <div class="wrap">
    <h2>すべての著作を一覧で見る</h2>
    <p>Amazonの著者検索ページから、ペーパーバック版を含む全著作をご覧いただけます。</p>
    <div class="cta-row">
      <a class="cta" href="{AUTHOR_JP}" target="_blank" rel="noopener">
        日本語：amazon.co.jp 著者ページ
      </a>
      <a class="cta outline" href="en.html">English books page</a>
    </div>
  </div>
</section>"""

    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<style>{CSS}
{OPTIN_CSS}
{REVIEW_CSS}
{EXTRA_CSS}</style>
</head>
<body>
{hero}
{optin_html}
{series_overview_html}
{review_cta_html}
{footer}

<div class="footer-meta">Last updated: {generated}</div>

</body>
</html>
"""


def main():
    books = load_books()
    print(f"Loaded {len(books)} published books from {BOOKS_DIR}")
    copied = sync_covers(books)
    print(f"Synced {copied} cover image(s) to {COVERS_DIR}")
    docs_dir = OUTPUT_PATH.parent
    docs_dir.mkdir(parents=True, exist_ok=True)
    # ① 日本語（index.html）と英語（en.html）を別ページで出力
    for lang, fname in (("jp", "index.html"), ("en", "en.html")):
        html_out = render_page(books, lang)
        out_path = docs_dir / fname
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        n = sum(1 for b in books
                if SERIES_CONFIG.get(b.get("series_id"), {}).get("lang") == lang)
        print(f"Wrote {out_path} ({len(html_out):,} bytes, {n} {lang} books)")


if __name__ == "__main__":
    main()
