#!/usr/bin/env python3
"""
generate_cv.py — hidenoritani.com CV（日本語 cv.html / 英語 cv_en.html）自動生成

研究業績（ORCID全件＋Crossref著者補完＋OpenAlex被引用）から日英2版のCVを生成する。
印刷最適化（A4）・言語トグル・ワンクリックPDF（window.print）付き。Wix iframe埋め込み前提。

- 計量指標は Google Scholar の実数値（2026-07-20 取得・出典明記）を採用。
- ネット取得は curl（この環境では python urllib が遮断される）。data/cache/ にキャッシュ。
- 職歴は「東大PD 2009–2012 → AIST 2012–2023 → 横浜薬科大 2023–」の訂正版（旧CVのAIST 2008–2023は誤り）。

使い方: python3 lib/generate_cv.py [--refresh]
"""
import json, os, subprocess, sys, urllib.parse
from html import escape

ORCID = "0000-0001-6390-4136"
MAILTO = "hidenori.tani@yok.hamayaku.ac.jp"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "data", "cache")
UA = "hidenoritani-hp/1.0 (mailto:%s)" % MAILTO
REFRESH = "--refresh" in sys.argv

ORCID_URL = "https://orcid.org/" + ORCID
SCHOLAR_URL = "https://scholar.google.com.au/citations?user=Y5we_eIAAAAJ&hl=en"
GITHUB_URL = "https://github.com/hidenori-tani"

# --- verified bibliometrics (Google Scholar, as of 2026-07-20) ---
METRICS = {"citations": "2,323", "h": "23", "i10": "34", "asof": "2026-07-20"}


def curl(url):
    return subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA, url],
                          capture_output=True, text=True, timeout=40).stdout


def cached(name, url):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p) and not REFRESH:
        return json.load(open(p))
    d = json.loads(curl(url))
    json.dump(d, open(p, "w"), ensure_ascii=False)
    return d


def initials(giv):
    return "".join(w[0] + "." for w in giv.replace("-", " ").replace(".", " ").split() if w) if giv else ""


def fetch():
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
                     "type": typ, "doi": doi, "volume": "", "authors": [], "cites": 0})
    # Crossref enrichment
    for p in rows:
        if not p["doi"]:
            continue
        try:
            m = cached("cr_" + p["doi"].replace("/", "_") + ".json",
                       "https://api.crossref.org/works/" + urllib.parse.quote(p["doi"]) + "?mailto=" + MAILTO)["message"]
            auth = []
            for a in m.get("author", []):
                fam = a.get("family", "") or ""; giv = a.get("given", "") or ""
                auth.append({"name": (fam + " " + initials(giv)).strip(), "pi": fam.strip().lower() == "tani"})
            if auth: p["authors"] = auth
            ct = m.get("container-title") or []
            if ct: p["journal"] = ct[0]
            tt = m.get("title") or []
            if tt: p["title"] = tt[0]
            p["volume"] = m.get("volume", "") or ""
            if not p["year"]:
                dp = (m.get("issued", {}).get("date-parts") or [[None]])[0]
                if dp and dp[0]: p["year"] = str(dp[0])
        except Exception:
            pass
    # OpenAlex citations
    dois = [p["doi"] for p in rows if p["doi"]]
    cites = {}
    for i in range(0, len(dois), 25):
        chunk = dois[i:i + 25]
        try:
            d2 = cached("oa_cites_%d.json" % i,
                        "https://api.openalex.org/works?filter=" +
                        urllib.parse.quote("doi:" + "|".join(chunk), safe=":|/.") +
                        "&per-page=50&select=doi,cited_by_count&mailto=" + MAILTO)
            for w in d2.get("results", []):
                cites[(w.get("doi") or "").replace("https://doi.org/", "").lower()] = w.get("cited_by_count", 0)
        except Exception:
            pass
    for p in rows:
        p["cites"] = cites.get((p["doi"] or "").lower(), 0)
    # selected = top 12 by citations
    ranked = sorted([p for p in rows if p["title"]], key=lambda p: p["cites"], reverse=True)[:12]
    sel = set(id(p) for p in ranked)
    for p in rows:
        p["selected"] = id(p) in sel and bool(p["doi"])
    return rows


def yk(r):
    try:
        return int(r["year"])
    except Exception:
        return -1


def authors_html(authors, etal_after=0):
    out = []
    for a in authors:
        nm = escape(a["name"])
        out.append("<b>" + nm + "</b>" if a["pi"] else nm)
    if etal_after and len(out) > etal_after:
        out = out[:etal_after] + ["et al."]
    return ", ".join(out)


def cite_line(p, etal=6):
    au = authors_html(p["authors"], etal_after=etal)
    au = (au + " ") if au else ""
    j = escape(p["journal"]); vol = escape(p["volume"]); yr = escape(p["year"])
    venue = "<span class='j'>" + j + "</span>" + ((" " + vol) if vol else "") + ((" (" + yr + ")") if yr else "")
    doi = ("<a href='https://doi.org/" + escape(p["doi"]) + "' target='_blank' rel='noopener'>doi:" +
           escape(p["doi"]) + "</a>") if p["doi"] else ""
    return au + "<span class='ti'>" + escape(p["title"]) + ".</span> " + venue + (". " + doi if doi else "")


# --- curated bilingual content (corrected career timeline) ---
CONTENT = {
    "ja": {
        "htmllang": "ja",
        "title": "略歴 / Curriculum Vitae — 谷英典",
        "meta": "谷英典（横浜薬科大学 准教授, Ph.D.）の詳細略歴。lncRNA・RNA安定性（BRIC-seq開発）・RNA創薬。査読論文62編・被引用2,323・h-index 23。",
        "name": "谷 英典", "en_name": "Hidenori Tani, Ph.D.",
        "role": "横浜薬科大学 薬学部 健康薬学科 准教授（2023年〜）",
        "affil": "Department of Health Pharmacy, Faculty of Pharmaceutical Sciences, Yokohama University of Pharmacy",
        "addr": "〒245-0066 神奈川県横浜市戸塚区俣野町601",
        "email_note": "（[at] を @ に置き換えてください）",
        "toggle_this": "日本語", "toggle_other": "English", "other_href": "cv_en.html",
        "print": "PDFで保存 / 印刷",
        "L": {"metrics": "研究指標", "summary": "研究概要", "interests": "研究分野",
              "education": "学歴", "appointments": "職歴", "method": "研究手法・貢献",
              "selected": "主要業績", "full": "全業績", "teaching": "教育", "service": "学会活動・査読",
              "grants": "研究費・受賞", "books": "一般向け著書"},
        "metrics_items": [("査読付き論文", "__PUBS__"), ("総被引用", METRICS["citations"]),
                          ("h-index", METRICS["h"]), ("i10-index", METRICS["i10"])],
        "metrics_src": "出典：Google Scholar（%s 時点）／論文数は ORCID" % METRICS["asof"],
        "summary": "専門は分子生物学、特に<b>長鎖ノンコーディングRNA（lncRNA）</b>の機能と代謝。細胞内RNAの安定性（半減期）を網羅的に測定する <b>BRIC-seq 法</b>を開発し、RNA分解を機能の一側面として捉える研究を展開している。近年は単一細胞での RNA turnover、RNA創薬、RNA生物学への計算・AI手法の応用にも取り組む。",
        "interests": ["長鎖ノンコーディングRNA（lncRNA）の機能と代謝",
                      "RNA安定性・半減期のゲノムワイド計測（BRIC-seq）",
                      "転写後制御・RNA分解経路", "単一細胞での RNA turnover",
                      "RNA創薬、および RNA生物学への計算・AI手法の応用"],
        "education": [("2008", "<b>博士（工学）</b>　早稲田大学大学院 理工学研究科",
                       "Ph.D. in Engineering, Waseda University"),
                      ("", "早稲田大学 理工学部 応用化学科（学部）",
                       "B.Eng., Applied Chemistry, Waseda University")],
        "appointments": [("2023 –", "<b>准教授</b>　横浜薬科大学 薬学部 健康薬学科",
                          "Associate Professor, Yokohama University of Pharmacy"),
                         ("2012 – 2023", "<b>研究員 → 主任研究員</b>　産業技術総合研究所（AIST）",
                          "Researcher / Senior Researcher, AIST"),
                         ("2009 – 2012", "<b>博士研究員（ポスドク）</b>　東京大学",
                          "Postdoctoral Researcher, University of Tokyo")],
        "method": "<b>BRIC-seq（5′-bromo-uridine immunoprecipitation chase sequencing）</b>を開発し、細胞内RNAの安定性（半減期）をゲノムワイドに測定する手法を確立。数百の短寿命ノンコーディング転写産物を同定した（<span class='j'>Genome Research</span>, 2012）。以後、RNA安定性を機能の指標として捉える研究を一貫して展開している。",
        "teaching_head": "横浜薬科大学 担当科目",
        "teaching": ["情報科学入門（1年次・必修）", "情報処理演習（1年次・必修）",
                     "生物系薬学演習1（4年次・必修）", "生物系実習II（2年次・必修／科目責任者）"],
        "service": ["査読：<i>Microbiology and Molecular Biology Reviews</i>（American Society for Microbiology）ほか"],
        "books_line": "一般読者・研究者・大学院生に向けた科学書・実用書を執筆。一覧は <a href='index.html' target='_blank' rel='noopener'>著書ページ</a>。",
        "full_note": "谷を太字で示す。完全な最新リストは <a href='publications.html' target='_blank' rel='noopener'>研究業績ページ</a> ／ <a href='%s' target='_blank' rel='noopener'>ORCID</a>。" % ORCID_URL,
        "asof": "As of " + METRICS["asof"],
        "idbtns": [("ORCID", ORCID_URL), ("Google Scholar", SCHOLAR_URL), ("GitHub", GITHUB_URL),
                   ("Publications", "publications.html"), ("Data & Code", "software.html")],
    },
    "en": {
        "htmllang": "en",
        "title": "Curriculum Vitae — Hidenori Tani",
        "meta": "CV of Hidenori Tani, Ph.D. (Associate Professor, Yokohama University of Pharmacy). lncRNA, RNA stability (BRIC-seq), RNA drug development. 62 papers, 2,323 citations, h-index 23.",
        "name": "Hidenori Tani", "en_name": "Ph.D. in Engineering",
        "role": "Associate Professor, Department of Health Pharmacy, Yokohama University of Pharmacy (2023– )",
        "affil": "Faculty of Pharmaceutical Sciences, Yokohama University of Pharmacy",
        "addr": "601 Matano-cho, Totsuka-ku, Yokohama 245-0066, Japan",
        "email_note": "(replace [at] with @)",
        "toggle_this": "English", "toggle_other": "日本語", "other_href": "cv.html",
        "print": "Save as PDF / Print",
        "L": {"metrics": "Metrics", "summary": "Research Summary", "interests": "Research Interests",
              "education": "Education", "appointments": "Appointments", "method": "Method & Contribution",
              "selected": "Selected Publications", "full": "Full Publication List", "teaching": "Teaching",
              "service": "Service & Peer Review", "grants": "Grants & Awards", "books": "Books (General Audience)"},
        "metrics_items": [("Publications", "__PUBS__"), ("Citations", METRICS["citations"]),
                          ("h-index", METRICS["h"]), ("i10-index", METRICS["i10"])],
        "metrics_src": "Source: Google Scholar (as of %s); publication count from ORCID" % METRICS["asof"],
        "summary": "Molecular biologist specializing in <b>long noncoding RNAs (lncRNAs)</b> and their metabolism. Developer of <b>BRIC-seq</b>, a genome-wide method for measuring intracellular RNA stability (half-life), used to study RNA degradation as a facet of function. Current work extends to single-cell RNA turnover, RNA drug development, and computational/AI approaches to RNA biology.",
        "interests": ["Function and metabolism of long noncoding RNAs (lncRNAs)",
                      "Genome-wide measurement of RNA stability / half-life (BRIC-seq)",
                      "Post-transcriptional regulation and RNA degradation pathways",
                      "Single-cell RNA turnover",
                      "RNA drug development; computational and AI approaches to RNA biology"],
        "education": [("2008", "<b>Ph.D. in Engineering</b>, Waseda University",
                       "早稲田大学大学院 理工学研究科"),
                      ("", "B.Eng., Applied Chemistry, Waseda University",
                       "早稲田大学 理工学部 応用化学科")],
        "appointments": [("2023 –", "<b>Associate Professor</b>, Yokohama University of Pharmacy",
                          "横浜薬科大学 薬学部 健康薬学科"),
                         ("2012 – 2023", "<b>Researcher → Senior Researcher</b>, AIST",
                          "産業技術総合研究所"),
                         ("2009 – 2012", "<b>Postdoctoral Researcher</b>, University of Tokyo",
                          "東京大学")],
        "method": "Developed <b>BRIC-seq (5′-bromo-uridine immunoprecipitation chase sequencing)</b>, establishing genome-wide measurement of intracellular RNA stability (half-life) and identifying hundreds of short-lived noncoding transcripts (<span class='j'>Genome Research</span>, 2012). Subsequent work consistently treats RNA stability as an indicator of function.",
        "teaching_head": "Courses taught, Yokohama University of Pharmacy",
        "teaching": ["Introduction to Information Science (1st year)",
                     "Information Processing Practicum (1st year)",
                     "Biological Pharmacy Seminar I (4th year)",
                     "Biology Laboratory II — immunology (2nd year; course coordinator)"],
        "service": ["Reviewer: <i>Microbiology and Molecular Biology Reviews</i> (American Society for Microbiology), among others"],
        "books_line": "Author of science and practical books for general readers, researchers, and graduate students. See the <a href='en.html' target='_blank' rel='noopener'>books page</a>.",
        "full_note": "Tani in bold. The complete, always-current list is on the <a href='publications.html' target='_blank' rel='noopener'>publications page</a> / <a href='%s' target='_blank' rel='noopener'>ORCID</a>." % ORCID_URL,
        "asof": "As of " + METRICS["asof"],
        "idbtns": [("ORCID", ORCID_URL), ("Google Scholar", SCHOLAR_URL), ("GitHub", GITHUB_URL),
                   ("Publications", "publications.html"), ("Data & Code", "software.html")],
    },
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=Raleway:wght@300;400;500;600&display=swap');
:root{--ink:#000;--ink-soft:#4d4d4d;--ink-mute:#888;--paper:#fff;--accent:#0057E1;--accent-soft:#4a85ea;--line:#e8e6e6;}
*{box-sizing:border-box;}
body{font-family:'Raleway',"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;color:var(--ink);background:#f4f4f5;margin:0;line-height:1.7;font-size:14px;}
h1,h2,h3{font-family:'Playfair Display',"Hiragino Mincho ProN","Yu Mincho",serif;font-weight:400;}
.toolbar{position:sticky;top:0;z-index:5;background:#f4f4f5;padding:12px 16px;max-width:840px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;}
.lang-nav{font-size:12px;letter-spacing:.06em;}
.lang-nav .active{color:var(--ink);border-bottom:1px solid var(--ink);padding-bottom:2px;margin-right:12px;}
.lang-nav a{color:var(--accent);text-decoration:none;}
.print-btn{font-family:'Raleway',sans-serif;font-size:12px;letter-spacing:.05em;color:#fff;background:var(--accent);border:none;padding:9px 18px;cursor:pointer;}
.print-btn:hover{background:var(--accent-soft);}
.sheet{max-width:840px;margin:0 auto 40px;background:var(--paper);padding:52px 60px 56px;box-shadow:0 4px 24px rgba(0,0,0,.07);}
.cv-head{border-bottom:2px solid var(--ink);padding-bottom:18px;}
.cv-head h1{font-size:36px;margin:0 0 2px;letter-spacing:.02em;}
.cv-head .en{font-family:'Playfair Display',serif;font-style:italic;font-size:16px;color:var(--ink-soft);margin-bottom:10px;}
.cv-head .role{font-size:13.5px;}
.cv-head .affil,.cv-head .addr{font-size:12.5px;color:var(--ink-soft);}
.contact{font-size:12px;color:var(--ink-soft);margin-top:8px;}
.id-row{margin-top:11px;display:flex;gap:7px;flex-wrap:wrap;}
.id-btn{display:inline-block;padding:6px 13px;border:1px solid var(--accent);color:var(--accent);text-decoration:none;font-size:11px;font-weight:500;letter-spacing:.04em;}
.id-btn:hover{background:var(--accent);color:#fff;}
.metrics{display:flex;gap:0;flex-wrap:wrap;margin:22px 0 6px;border:1px solid var(--line);}
.metric{flex:1;min-width:110px;text-align:center;padding:14px 8px;border-right:1px solid var(--line);}
.metric:last-child{border-right:none;}
.metric .num{font-family:'Playfair Display',serif;font-size:26px;color:var(--accent);line-height:1;}
.metric .lab{font-size:10.5px;letter-spacing:.1em;color:var(--ink-mute);text-transform:uppercase;margin-top:6px;}
.metric-src{font-size:10.5px;color:var(--ink-mute);text-align:right;margin:4px 0 0;}
section.blk{margin-top:26px;}
.blk h2{font-size:12px;letter-spacing:.2em;color:var(--ink-mute);font-family:'Raleway',sans-serif;font-weight:600;border-bottom:1px solid var(--line);padding-bottom:5px;margin:0 0 12px;text-transform:uppercase;}
.blk h2 .jp{font-family:'Hiragino Sans',sans-serif;letter-spacing:.05em;margin-left:8px;color:var(--ink-soft);}
.row{display:grid;grid-template-columns:110px 1fr;gap:12px;margin-bottom:9px;}
.row .yr{color:var(--ink-mute);font-size:12.5px;}
.row .what b{font-weight:600;}
.row .what .sub{color:var(--ink-mute);font-size:11.5px;}
ul.plain{margin:0;padding-left:17px;}
ul.plain li{margin-bottom:5px;}
.pub{margin-bottom:10px;font-size:13px;line-height:1.55;}
.pub .num-c{color:var(--ink-mute);font-size:11px;}
.pub b{font-weight:600;}
.pub .ti{}
.pub .j{font-style:italic;color:var(--ink-soft);}
.pub a{color:var(--accent-soft);text-decoration:none;}
.pub a:hover{text-decoration:underline;}
ol.sel{margin:0;padding-left:20px;}
ol.sel li{margin-bottom:10px;font-size:13px;line-height:1.55;}
.year-h{font-family:'Playfair Display',serif;font-size:17px;margin:16px 0 6px;color:var(--ink);}
.note{font-size:11.5px;color:var(--ink-mute);margin-top:8px;}
.note a,.books a,.blk a.inl{color:var(--accent);text-decoration:none;}
.asof{color:#bbb;font-size:11px;margin-top:30px;text-align:right;letter-spacing:.05em;}
@media(max-width:600px){.sheet{padding:30px 20px;}.cv-head h1{font-size:28px;}.row{grid-template-columns:84px 1fr;}.metric .num{font-size:21px;}}
@media print{
  @page{size:A4;margin:15mm 14mm;}
  body{background:#fff;font-size:9.6pt;line-height:1.5;}
  .toolbar{display:none;}
  .sheet{box-shadow:none;max-width:none;margin:0;padding:0;}
  .id-btn{border-color:#999;color:#000;}
  a{color:#000 !important;}
  section.blk{break-inside:avoid;}
  .pub,ol.sel li{break-inside:avoid;}
}
"""


def render(c, works):
    total = len([w for w in works])
    L = c["L"]

    def h2(key):
        # bilingual header: primary label + faint secondary
        return "<h2>" + escape(L[key]) + "</h2>"

    # metrics
    mi = []
    for lab, val in c["metrics_items"]:
        v = str(total) if val == "__PUBS__" else val
        mi.append("<div class='metric'><div class='num'>" + escape(v) + "</div><div class='lab'>" + escape(lab) + "</div></div>")
    metrics = "<div class='metrics'>" + "".join(mi) + "</div><div class='metric-src'>" + escape(c["metrics_src"]) + "</div>"

    interests = "<ul class='plain'>" + "".join("<li>" + escape(x) + "</li>" for x in c["interests"]) + "</ul>"

    def rows(items):
        out = []
        for yr, what, sub in items:
            out.append("<div class='row'><div class='yr'>" + escape(yr) + "</div><div class='what'>" +
                       what + ("<div class='sub'>" + escape(sub) + "</div>" if sub else "") + "</div></div>")
        return "".join(out)

    # selected
    ranked = sorted([w for w in works if w.get("selected")], key=lambda w: w["cites"], reverse=True)
    sel_html = "<ol class='sel'>" + "".join("<li>" + cite_line(w) + "</li>" for w in ranked) + "</ol>"

    # full by year
    yrs = sorted({yk(w) for w in works if yk(w) > 0}, reverse=True)
    blocks = []
    for y in yrs:
        items = [w for w in works if yk(w) == y]
        lis = "".join("<div class='pub'>" + cite_line(w, etal=8) + "</div>" for w in items)
        blocks.append("<div class='year-h'>" + str(y) + "</div>" + lis)
    full_html = "".join(blocks)

    teaching = ("<div style='font-size:12px;color:var(--ink-soft);margin-bottom:6px;'>" + escape(c["teaching_head"]) +
                "</div><ul class='plain'>" + "".join("<li>" + escape(x) + "</li>" for x in c["teaching"]) + "</ul>")
    service = "<ul class='plain'>" + "".join("<li>" + x + "</li>" for x in c["service"]) + "</ul>"
    books = "<div class='books'>" + c["books_line"] + "</div>"

    idbtns = "".join("<a class='id-btn' href='" + escape(u) + "'" +
                     (" target='_blank' rel='noopener'" if u.startswith("http") else "") + ">" + escape(t) + "</a>"
                     for t, u in c["idbtns"])

    html = """<!DOCTYPE html>
<html lang="__LANG__">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="description" content="__META__">
<style>__CSS__</style>
</head>
<body>
<div class="toolbar">
  <div class="lang-nav"><span class="active">__THIS__</span><a href="__OTHERHREF__">__OTHER__</a></div>
  <button class="print-btn" onclick="window.print()">__PRINT__</button>
</div>
<div class="sheet">
  <div class="cv-head">
    <h1>__NAME__</h1>
    <div class="en">__ENNAME__</div>
    <div class="role">__ROLE__</div>
    <div class="affil">__AFFIL__</div>
    <div class="addr">__ADDR__</div>
    <div class="contact">Email: hidenori.tani[at]yok.hamayaku.ac.jp __EMAILNOTE__　·　ORCID: __ORCIDID__</div>
    <div class="id-row">__IDBTNS__</div>
  </div>
  __METRICS__
  <section class="blk">__H_SUMMARY__<div>__SUMMARY__</div></section>
  <section class="blk">__H_INTERESTS__ __INTERESTS__</section>
  <section class="blk">__H_APPTS__ __APPTS__</section>
  <section class="blk">__H_EDU__ __EDU__</section>
  <section class="blk">__H_METHOD__<div>__METHOD__</div></section>
  <section class="blk">__H_SELECTED__ __SELECTED__</section>
  <section class="blk">__H_TEACHING__ __TEACHING__</section>
  <section class="blk">__H_SERVICE__ __SERVICE__</section>
  <section class="blk">__H_BOOKS__ __BOOKS__</section>
  <section class="blk">__H_FULL__ __FULL__<div class="note">__FULLNOTE__</div></section>
  <div class="asof">__ASOF__</div>
</div>
</body>
</html>"""
    repl = {
        "__LANG__": c["htmllang"], "__TITLE__": escape(c["title"]), "__META__": escape(c["meta"]),
        "__CSS__": CSS, "__THIS__": escape(c["toggle_this"]), "__OTHER__": escape(c["toggle_other"]),
        "__OTHERHREF__": c["other_href"], "__PRINT__": escape(c["print"]),
        "__NAME__": escape(c["name"]), "__ENNAME__": escape(c["en_name"]), "__ROLE__": escape(c["role"]),
        "__AFFIL__": escape(c["affil"]), "__ADDR__": escape(c["addr"]), "__EMAILNOTE__": escape(c["email_note"]),
        "__ORCIDID__": ORCID, "__IDBTNS__": idbtns, "__METRICS__": metrics,
        "__H_SUMMARY__": h2("summary"), "__SUMMARY__": c["summary"],
        "__H_INTERESTS__": h2("interests"), "__INTERESTS__": interests,
        "__H_APPTS__": h2("appointments"), "__APPTS__": rows(c["appointments"]),
        "__H_EDU__": h2("education"), "__EDU__": rows(c["education"]),
        "__H_METHOD__": h2("method"), "__METHOD__": c["method"],
        "__H_SELECTED__": h2("selected"), "__SELECTED__": sel_html,
        "__H_TEACHING__": h2("teaching"), "__TEACHING__": teaching,
        "__H_SERVICE__": h2("service"), "__SERVICE__": service,
        "__H_BOOKS__": h2("books"), "__BOOKS__": books,
        "__H_FULL__": h2("full"), "__FULL__": full_html, "__FULLNOTE__": c["full_note"],
        "__ASOF__": escape(c["asof"]),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html


if __name__ == "__main__":
    works = fetch()
    for lang, fn in (("ja", "cv.html"), ("en", "cv_en.html")):
        out = os.path.join(HERE, "docs", fn)
        open(out, "w").write(render(CONTENT[lang], works))
        print("wrote", out)
    print("works:", len(works), "| selected:", sum(1 for w in works if w.get("selected")))
