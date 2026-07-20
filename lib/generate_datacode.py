#!/usr/bin/env python3
"""
generate_datacode.py — hidenoritani.com Data & Code / Software ページ自動生成

GitHub 公開リポジトリ（谷英典の再現コード）＋ 本人帰属を機械検証した Zenodo アーカイブから
docs/software.html を生成する。Wix の iframe 埋め込み前提。

- 生成物は software.html のみ。書籍ページ・業績ページには触れない。
- Zenodo は creators を確認済みの DOI のみ掲載（RNAdecayCafe 等の他者作は除外）。
- 取得は curl（この環境では python urllib が遮断されるため）。data/cache/ にキャッシュ。

使い方:
  python3 lib/generate_datacode.py [--refresh]
"""
import json, os, subprocess, sys
from html import escape

GH_USER = "hidenori-tani"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "data", "cache")
OUT = os.path.join(HERE, "docs", "software.html")
UA = "hidenoritani-hp/1.0"
REFRESH = "--refresh" in sys.argv

ORCID_URL = "https://orcid.org/0000-0001-6390-4136"
SCHOLAR_URL = "https://scholar.google.com.au/citations?user=Y5we_eIAAAAJ&hl=en"
GITHUB_URL = "https://github.com/" + GH_USER

# website itself — not a research artifact
EXCLUDE = {"hp_books_site"}

# Zenodo DOI → repo name. Creators machine-verified as "Tani, Hidenori" (2026-07-20).
REPO_ZENODO = {
    "paper-lncrna-liver-singlecell-dry": "10.5281/zenodo.21025051",
    "rmst-cell-of-origin": "10.5281/zenodo.21366063",
}
# Verified Zenodo deposits without a matching public repo (code+data archived directly).
STANDALONE_ZENODO = [
    {"doi": "10.5281/zenodo.21297535",
     "title": "A universal RNA stability code operates across single-cell states",
     "date": "2026-07-10"},
]


def curl(url):
    return subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA, url],
                          capture_output=True, text=True, timeout=40).stdout


def cached_json(name, url):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and not REFRESH:
        return json.load(open(path))
    d = json.loads(curl(url))
    json.dump(d, open(path, "w"), ensure_ascii=False)
    return d


def readme_h1(name, default_branch):
    """First-level heading from README as a description fallback."""
    import re
    for br in (default_branch, "main", "master"):
        for fn in ("README.md", "readme.md"):
            path = os.path.join(CACHE, "readme_%s_%s_%s" % (name, br, fn.replace(".", "_")))
            if os.path.exists(path) and not REFRESH:
                t = open(path).read()
            else:
                t = curl("https://raw.githubusercontent.com/%s/%s/%s/%s" % (GH_USER, name, br, fn))
                if t:
                    open(path, "w").write(t)
            if t and "404: Not Found" not in t[:40]:
                m = re.search(r'^#[ \t]+([^#\n].*)$', t, re.M)
                if m:
                    return m.group(1).strip()
    return ""


def fetch_repos():
    d = cached_json("gh_repos.json",
                    "https://api.github.com/users/%s/repos?per_page=100&sort=pushed" % GH_USER)
    repos = []
    for r in d:
        if r["name"] in EXCLUDE:
            continue
        desc = (r.get("description") or "").strip()
        if not desc:
            desc = readme_h1(r["name"], r.get("default_branch", "main"))
        repos.append({
            "name": r["name"],
            "desc": desc,
            "lang": r.get("language") or "",
            "url": r["html_url"],
            "pushed": (r.get("pushed_at") or "")[:10],
        })
    return repos


def render(repos):
    cards = []
    for r in repos:
        z = REPO_ZENODO.get(r["name"])
        lang = ("<span class='lang'>" + escape(r["lang"]) + "</span>") if r["lang"] else ""
        zbadge = ("<a class='zbadge' href='https://doi.org/" + escape(z) +
                  "' target='_blank' rel='noopener'>Zenodo · " + escape(z.split('.')[-1]) + "</a>") if z else ""
        cards.append(
            "<li class='repo'>"
            "<div class='repo-head'><a class='repo-name' href='" + escape(r["url"]) +
            "' target='_blank' rel='noopener'>" + escape(r["name"]) + "</a>" + lang + "</div>"
            "<div class='repo-desc'>" + escape(r["desc"] or "—") + "</div>"
            "<div class='repo-meta'>"
            "<a class='gh' href='" + escape(r["url"]) + "' target='_blank' rel='noopener'>View on GitHub</a>" +
            (" · " + zbadge if zbadge else "") +
            ("<span class='pushed'>updated " + escape(r["pushed"]) + "</span>" if r["pushed"] else "") +
            "</div></li>")

    zlist = []
    for z in STANDALONE_ZENODO:
        zlist.append(
            "<li class='repo'>"
            "<div class='repo-head'><a class='repo-name' href='https://doi.org/" + escape(z["doi"]) +
            "' target='_blank' rel='noopener'>" + escape(z["title"]) + "</a></div>"
            "<div class='repo-meta'><a class='zbadge' href='https://doi.org/" + escape(z["doi"]) +
            "' target='_blank' rel='noopener'>Zenodo · " + escape(z["doi"].split('.')[-1]) + "</a>"
            "<span class='pushed'>" + escape(z["date"]) + "</span></div></li>")

    standalone_section = ("""
  <div class="section-label">ARCHIVED DATA &amp; CODE</div>
  <h2 class="sec">Zenodo アーカイブ</h2>
  <p class="sec-lead">論文に紐づくコード・データの恒久アーカイブ（DOI 付き）。掲載は creators を確認済みの寄託のみです。</p>
  <ol class="repo-list">__ZLIST__</ol>""".replace("__ZLIST__", "".join(zlist))) if zlist else ""

    tmpl = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>データとコード / Data &amp; Code — 谷英典</title>
<meta name="description" content="谷英典（横浜薬科大学）の研究再現用コード・データ一覧。lncRNA解析・RNA安定性・単一細胞再解析のGitHubリポジトリとZenodoアーカイブ。">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=Raleway:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--ink:#000;--ink-soft:#4d4d4d;--ink-mute:#888;--paper:#fff;--accent:#0057E1;--accent-soft:#4a85ea;--line:#e8e6e6;}
*{box-sizing:border-box;}
body{font-family:'Raleway',"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;color:var(--ink);background:var(--paper);margin:0;line-height:1.79;font-size:15px;}
.wrap{max-width:900px;margin:0 auto;padding:0 24px;}
h1,h2,h3{font-family:'Playfair Display',"Hiragino Mincho ProN","Yu Mincho",serif;font-weight:400;}
.hero{text-align:center;padding:72px 24px 40px;border-bottom:1px solid var(--line);}
.lang-nav{display:flex;justify-content:center;gap:20px;margin-bottom:24px;font-size:13px;letter-spacing:.08em;}
.lang-nav .active{color:var(--ink);border-bottom:1px solid var(--ink);padding-bottom:2px;}
.hero h1{font-size:44px;margin:0 0 6px;line-height:1.3;}
.hero .sub-en{font-family:'Playfair Display',serif;font-style:italic;font-size:19px;color:var(--ink-soft);letter-spacing:.08em;margin-bottom:22px;}
.hero .lead{max-width:640px;margin:0 auto 26px;color:var(--ink-soft);font-size:14px;}
.id-row{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;}
.id-btn{display:inline-block;padding:9px 18px;border:1px solid var(--accent);color:var(--accent);text-decoration:none;font-size:12px;font-weight:500;letter-spacing:.06em;transition:.2s;}
.id-btn:hover{background:var(--accent);color:#fff;}
.section-label{text-align:center;font-size:12px;font-weight:500;letter-spacing:.3em;color:var(--ink-mute);margin:44px 0 6px;}
h2.sec{text-align:center;font-size:26px;margin:0 0 8px;}
.sec-lead{text-align:center;color:var(--ink-soft);font-size:13px;max-width:620px;margin:0 auto 26px;}
.repo-list{list-style:none;margin:0;padding:0;display:grid;gap:14px;}
.repo{border:1px solid var(--line);padding:20px 22px;transition:box-shadow .25s,border-color .25s;}
.repo:hover{box-shadow:0 8px 22px rgba(0,0,0,.06);border-color:var(--accent);}
.repo-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px;}
.repo-name{font-family:'JetBrains Mono',monospace;font-size:15px;color:var(--accent);text-decoration:none;font-weight:500;}
.repo-name:hover{text-decoration:underline;}
.lang{font-size:11px;letter-spacing:.06em;color:var(--ink-mute);border:1px solid var(--line);border-radius:3px;padding:1px 7px;}
.repo-desc{font-size:14px;color:var(--ink);line-height:1.65;margin-bottom:10px;}
.repo-meta{font-size:12px;color:var(--ink-mute);display:flex;gap:10px;flex-wrap:wrap;align-items:center;}
.repo-meta .gh{color:var(--accent-soft);text-decoration:none;}
.repo-meta .gh:hover{text-decoration:underline;}
.zbadge{color:#fff;background:var(--accent-soft);text-decoration:none;padding:2px 8px;border-radius:3px;font-size:11px;letter-spacing:.03em;}
.zbadge:hover{background:var(--accent);}
.pushed{margin-left:auto;color:#bbb;}
.foot{text-align:center;padding:44px 24px 30px;border-top:1px solid var(--line);margin-top:36px;color:var(--ink-mute);font-size:12px;}
.foot a{color:var(--accent);text-decoration:none;}
.footer-meta{text-align:center;color:#bbb;font-size:11px;padding:0 0 26px;letter-spacing:.05em;}
@media(max-width:600px){.hero h1{font-size:34px;}.wrap{padding:0 18px;}.pushed{margin-left:0;}}
</style>
</head>
<body>
<div class="hero">
  <div class="wrap">
    <div class="lang-nav"><span class="active">データとコード</span></div>
    <h1>データとコード</h1>
    <div class="sub-en">Data &amp; Code</div>
    <p class="lead">私の研究は、公開データの再解析と、その手続きを誰でも再現できる形で残すことを重視しています。論文に対応する解析コード・データを GitHub と Zenodo で公開しています。</p>
    <div class="id-row">
      <a class="id-btn" href="__GITHUB__" target="_blank" rel="noopener">GitHub</a>
      <a class="id-btn" href="__ORCID__" target="_blank" rel="noopener">ORCID</a>
      <a class="id-btn" href="__SCHOLAR__" target="_blank" rel="noopener">Google Scholar</a>
    </div>
  </div>
</div>
<div class="wrap">
  <div class="section-label">CODE REPOSITORIES</div>
  <h2 class="sec">再現コード（GitHub）</h2>
  <p class="sec-lead">各論文の解析を再現するためのコードとデータ。__NREPO__ リポジトリを公開しています。</p>
  <ol class="repo-list">__CARDS__</ol>
__STANDALONE__
  <div class="foot">
    最新の全リポジトリは <a href="__GITHUB__" target="_blank" rel="noopener">github.com/hidenori-tani</a> でご覧いただけます。<br>
    本ページは GitHub 公開API＋Zenodo から自動生成しています（creators 確認済みの寄託のみ掲載）。
  </div>
  <div class="footer-meta">Generated: __GEN__ · Source: GitHub · Zenodo</div>
</div>
</body>
</html>"""
    gen = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    html = (tmpl
            .replace("__CARDS__", "".join(cards))
            .replace("__STANDALONE__", standalone_section)
            .replace("__NREPO__", str(len(repos)))
            .replace("__ORCID__", ORCID_URL)
            .replace("__SCHOLAR__", SCHOLAR_URL)
            .replace("__GITHUB__", GITHUB_URL)
            .replace("__GEN__", gen))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(html)
    return len(repos)


if __name__ == "__main__":
    repos = fetch_repos()
    n = render(repos)
    print("wrote %s  (%d repos + %d standalone zenodo)" % (OUT, n, len(STANDALONE_ZENODO)))
