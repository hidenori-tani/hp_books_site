#!/usr/bin/env python3
"""
generate_publications.py — hidenoritani.com 業績一覧ページ自動生成

ORCID 公開API（全業績）＋ Crossref（DOIから著者・誌名補完）から
docs/publications.html を生成する。Wix の iframe で埋め込む前提。

- 生成物は publications.html のみ。書籍ページ（index.html/en.html）には一切触れない。
- 谷英典（Tani）を著者リストで太字化。
- ネットワーク取得は curl 経由（この環境では python urllib が遮断されるため）。
  取得結果は data/cache/ にキャッシュし、--refresh で再取得。

使い方:
  python3 lib/generate_publications.py            # キャッシュ利用（無ければ取得）
  python3 lib/generate_publications.py --refresh  # ORCID/Crossref を再取得
"""
import json, os, subprocess, sys, urllib.parse
from html import escape

ORCID = "0000-0001-6390-4136"
MAILTO = "hidenori.tani@yok.hamayaku.ac.jp"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "data", "cache")
OUT = os.path.join(HERE, "docs", "publications.html")
UA = "hidenoritani-hp/1.0 (mailto:%s)" % MAILTO
REFRESH = "--refresh" in sys.argv

# 谷先生の識別子（実名①軸のみ・§4）
ORCID_URL = "https://orcid.org/" + ORCID
SCHOLAR_URL = "https://scholar.google.com.au/citations?user=Y5we_eIAAAAJ&hl=en"
GITHUB_URL = "https://github.com/hidenori-tani"


def curl_json(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA, url],
                       capture_output=True, text=True, timeout=40)
    return json.loads(r.stdout)


def cached(name, url):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and not REFRESH:
        return json.load(open(path))
    data = curl_json(url)
    json.dump(data, open(path, "w"), ensure_ascii=False)
    return data


def initials(giv):
    if not giv:
        return ""
    return "".join(w[0] + "." for w in giv.replace("-", " ").replace(".", " ").split() if w)


def fetch_orcid():
    d = cached("orcid_works.json", "https://pub.orcid.org/v3.0/%s/works" % ORCID)
    rows = []
    for g in d.get("group", []):
        ws = g.get("work-summary", [{}])[0]
        title = (((ws.get("title") or {}).get("title") or {}) or {}).get("value", "")
        journal = (ws.get("journal-title") or {}).get("value", "")
        year = ((ws.get("publication-date") or {}).get("year") or {}).get("value", "")
        typ = ws.get("type", "") or ""
        doi = ""
        for eid in ((ws.get("external-ids") or {}).get("external-id") or []):
            if eid.get("external-id-type") == "doi":
                doi = eid.get("external-id-value", ""); break
        rows.append({"year": year, "title": title.strip(), "journal": journal.strip(),
                     "type": typ, "doi": doi, "volume": "", "authors": []})
    return rows


def enrich(rows):
    for p in rows:
        if not p["doi"]:
            continue
        try:
            m = cached("cr_" + p["doi"].replace("/", "_") + ".json",
                       "https://api.crossref.org/works/" + urllib.parse.quote(p["doi"]) + "?mailto=" + MAILTO)["message"]
            auth = []
            for a in m.get("author", []):
                fam = a.get("family", "") or ""; giv = a.get("given", "") or ""
                nm = (fam + " " + initials(giv)).strip()
                auth.append({"name": nm, "pi": fam.strip().lower() == "tani"})
            if auth:
                p["authors"] = auth
            ct = m.get("container-title") or []
            if ct: p["journal"] = ct[0]
            tt = m.get("title") or []
            if tt: p["title"] = tt[0]
            p["volume"] = m.get("volume", "") or ""
            if not p["year"]:
                dp = (m.get("issued", {}).get("date-parts") or [[None]])[0]
                if dp and dp[0]:
                    p["year"] = str(dp[0])
        except Exception:
            pass
    return rows


def yk(r):
    try:
        return int(r["year"])
    except Exception:
        return -1


def author_html(authors):
    parts = []
    for a in authors:
        nm = escape(a["name"])
        parts.append("<b>" + nm + "</b>" if a["pi"] else nm)
    return ", ".join(parts)


def render(rows):
    rows.sort(key=lambda r: (yk(r), r["title"]), reverse=True)
    years = sorted({yk(r) for r in rows if yk(r) > 0}, reverse=True)
    total = len(rows)
    yr_lo = min(y for y in years); yr_hi = max(y for y in years)

    blocks = []
    for y in years:
        items = [r for r in rows if yk(r) == y]
        lis = []
        for r in items:
            ah = author_html(r["authors"])
            title = escape(r["title"])
            jr = escape(r["journal"])
            vol = escape(r["volume"])
            venue = jr + ((" <span class='vol'>" + vol + "</span>") if vol else "")
            doi = r["doi"]
            doi_html = ("<a class='doi' href='https://doi.org/" + escape(doi) +
                        "' target='_blank' rel='noopener'>doi:" + escape(doi) + "</a>") if doi else ""
            is_preprint = (r.get("type") or "").lower() in ("working-paper", "preprint", "posted-content")
            badge = "<span class='badge'>Preprint</span>" if is_preprint else ""
            meta = " · ".join(x for x in [("<span class='venue'>" + venue + "</span>" if venue else ""), doi_html] if x)
            au = ("<div class='au'>" + ah + "</div>") if ah else ""
            lis.append(
                "<li class='pub'>" + au +
                "<div class='ti'>" + badge + title + "</div>" +
                ("<div class='meta'>" + meta + "</div>" if meta else "") +
                "</li>")
        blocks.append(
            "<section class='year-block'><div class='year-head'>" + str(y) +
            "<span class='year-count'>" + str(len(items)) + "</span></div>" +
            "<ol class='pub-list'>" + "".join(lis) + "</ol></section>")

    tmpl = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>研究業績 / Publications — 谷英典</title>
<meta name="description" content="谷英典（横浜薬科大学准教授）の査読付き論文一覧。lncRNA・RNA安定性・RNA創薬を中心に__TOTAL__編。ORCID・Google Scholar・Crossref連携。">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=Raleway:wght@300;400;500;600&display=swap');
:root{--ink:#000;--ink-soft:#4d4d4d;--ink-mute:#888;--paper:#fff;--accent:#0057E1;--accent-soft:#4a85ea;--line:#e8e6e6;}
*{box-sizing:border-box;}
body{font-family:'Raleway',"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;color:var(--ink);background:var(--paper);margin:0;line-height:1.79;font-size:15px;font-weight:400;}
.wrap{max-width:900px;margin:0 auto;padding:0 24px;}
h1,h2,h3{font-family:'Playfair Display',"Hiragino Mincho ProN","Yu Mincho",serif;font-weight:400;}
.hero{text-align:center;padding:72px 24px 40px;border-bottom:1px solid var(--line);}
.lang-nav{display:flex;justify-content:center;gap:20px;margin-bottom:24px;font-family:'Raleway',sans-serif;font-size:13px;letter-spacing:.08em;}
.lang-nav .active{color:var(--ink);border-bottom:1px solid var(--ink);padding-bottom:2px;}
.hero h1{font-size:44px;margin:0 0 6px;line-height:1.3;letter-spacing:.01em;}
.hero .sub-en{font-family:'Playfair Display',serif;font-style:italic;font-size:19px;color:var(--ink-soft);letter-spacing:.08em;margin-bottom:22px;}
.hero .lead{max-width:620px;margin:0 auto 26px;color:var(--ink-soft);font-size:14px;}
.id-row{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;}
.id-btn{display:inline-block;padding:9px 18px;border:1px solid var(--accent);color:var(--accent);text-decoration:none;font-size:12px;font-weight:500;letter-spacing:.06em;transition:.2s;}
.id-btn:hover{background:var(--accent);color:#fff;}
.summary{text-align:center;padding:26px 24px 4px;color:var(--ink-mute);font-size:12px;letter-spacing:.12em;}
.year-block{padding:8px 0 4px;}
.year-head{font-family:'Playfair Display',serif;font-size:26px;color:var(--ink);border-bottom:1px solid var(--line);padding:22px 0 8px;margin:14px 0 4px;display:flex;align-items:baseline;gap:12px;}
.year-count{font-family:'Raleway',sans-serif;font-size:11px;color:var(--ink-mute);letter-spacing:.1em;}
.pub-list{list-style:none;margin:0;padding:0;}
.pub{padding:16px 0;border-bottom:1px solid #f1efef;}
.pub .au{font-size:13px;color:var(--ink-soft);margin-bottom:3px;}
.pub .au b{color:var(--ink);font-weight:600;}
.pub .ti{font-size:15px;color:var(--ink);line-height:1.6;}
.pub .badge{display:inline-block;font-size:10px;letter-spacing:.08em;color:var(--ink-mute);border:1px solid var(--line);border-radius:3px;padding:1px 6px;margin-right:8px;vertical-align:middle;font-family:'Raleway',sans-serif;}
.pub .meta{font-size:12.5px;color:var(--ink-mute);margin-top:4px;}
.pub .venue{font-style:italic;color:var(--ink-soft);}
.pub .vol{font-style:normal;}
.pub .doi{color:var(--accent-soft);text-decoration:none;}
.pub .doi:hover{text-decoration:underline;}
.foot{text-align:center;padding:40px 24px 30px;border-top:1px solid var(--line);margin-top:20px;color:var(--ink-mute);font-size:12px;}
.foot a{color:var(--accent);text-decoration:none;}
.footer-meta{text-align:center;color:#bbb;font-size:11px;padding:0 0 26px;letter-spacing:.05em;}
@media(max-width:600px){.hero h1{font-size:34px;}.wrap{padding:0 18px;}}
</style>
</head>
<body>
<div class="hero">
  <div class="wrap">
    <div class="lang-nav"><span class="active">研究業績</span></div>
    <h1>研究業績</h1>
    <div class="sub-en">Publications</div>
    <p class="lead">長鎖ノンコーディングRNA（lncRNA）の機能・RNA安定性・RNA創薬を中心とする査読付き論文の一覧です。下記リンクから ORCID / Google Scholar の常に最新のリストもご覧いただけます。</p>
    <div class="id-row">
      <a class="id-btn" href="__ORCID__" target="_blank" rel="noopener">ORCID</a>
      <a class="id-btn" href="__SCHOLAR__" target="_blank" rel="noopener">Google Scholar</a>
      <a class="id-btn" href="__GITHUB__" target="_blank" rel="noopener">GitHub</a>
    </div>
  </div>
</div>
<div class="summary">__TOTAL__ PUBLICATIONS · __LO__–__HI__</div>
<div class="wrap">
__BLOCKS__
  <div class="foot">
    最新の完全な業績リストは
    <a href="__ORCID__" target="_blank" rel="noopener">ORCID</a> ・
    <a href="__SCHOLAR__" target="_blank" rel="noopener">Google Scholar</a>
    でご覧いただけます。<br>
    本リストは ORCID 公開API＋Crossref から自動生成しています。
  </div>
  <div class="footer-meta">Generated: __GEN__ · Source: ORCID · Crossref</div>
</div>
</body>
</html>"""
    gen = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    html = (tmpl
            .replace("__BLOCKS__", "\n".join(blocks))
            .replace("__TOTAL__", str(total))
            .replace("__LO__", str(yr_lo))
            .replace("__HI__", str(yr_hi))
            .replace("__ORCID__", ORCID_URL)
            .replace("__SCHOLAR__", SCHOLAR_URL)
            .replace("__GITHUB__", GITHUB_URL)
            .replace("__GEN__", gen))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(html)
    return total, yr_lo, yr_hi


if __name__ == "__main__":
    rows = enrich(fetch_orcid())
    total, lo, hi = render(rows)
    print("wrote %s  (%d pubs, %d-%d)" % (OUT, total, lo, hi))
    print("with authors:", sum(1 for r in rows if r["authors"]))
