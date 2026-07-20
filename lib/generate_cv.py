#!/usr/bin/env python3
"""
generate_cv.py — hidenoritani.com CV（日本語 cv.html / 英語 cv_en.html）自動生成

一次ソース：lib/cv_source_data.py（先生の研究室ページの正式業績・2026-07-20提供）。
原著49・総説22・外部グラント8・招待講演19 を全掲載＋主要12＋研究指標。
印刷最適化（A4）・言語トグル・window.print()。Wix iframe 埋め込み前提。

計量指標は Google Scholar 実数値（2026-07-20・出典明記）。
職歴：東大PD 2009–2012 → AIST 2012–2023 → 横浜薬科大 2023–。

使い方: python3 lib/generate_cv.py
"""
import os, sys, re
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv_source_data as D

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORCID = "0000-0001-6390-4136"
ORCID_URL = "https://orcid.org/" + ORCID
SCHOLAR_URL = "https://scholar.google.com.au/citations?user=Y5we_eIAAAAJ&hl=en"
GITHUB_URL = "https://github.com/hidenori-tani"
METRICS = {"citations": "2,323", "h": "23", "i10": "34", "asof": "2026-07-20"}
N_ORIG = len(D.ORIGINALS)
N_REV = len(D.REVIEWS_EN) + len(D.REVIEWS_JP)


def bold_pi(s):
    # s is already HTML-escaped; PI tokens contain no special chars
    s = s.replace("Tani H", "<b>Tani H</b>")
    s = s.replace("谷英典", "<b>谷英典</b>")
    return s


def cite(authors, title, venue, year, star=False):
    a = bold_pi(escape(authors))
    t = escape(title)
    v = escape(venue)
    y = (" (" + escape(str(year)) + ")") if year else ""
    badge = "<span class='star'>&#9733;</span>" if star else ""
    return badge + a + " <span class='ti'>" + t + "</span> <span class='j'>" + v + "</span>" + y + "."


def pub_ol(items, numbered_from=None):
    lis = "".join("<li>" + cite(a, t, v, y, star) + "</li>" for (n, y, a, t, v, star) in items)
    return "<ol class='sel'>" + lis + "</ol>"


def originals_by_year():
    items = sorted(D.ORIGINALS, key=lambda o: (o[1], o[0]), reverse=True)
    return "".join("<div class='pub'>" + cite(a, t, v, y, star) + "</div>" for (n, y, a, t, v, star) in items)


def reviews_block(items, jp=False):
    out = []
    for row in items:
        n, y, a, t, v = row
        out.append("<div class='pub'>" + cite(a, t, v, y) + "</div>")
    return "".join(out)


def grants_rows(lang):
    out = []
    for yr, ja, en in D.GRANTS:
        main = ja if lang == "ja" else en
        sub = en if lang == "ja" else ja
        out.append("<div class='row'><div class='yr'>" + escape(yr) + "</div><div class='what'>" +
                   escape(main) + "<div class='sub'>" + escape(sub) + "</div></div></div>")
    return "".join(out)


def talks_block(lang):
    out = ["<div class='talk-sub'>" + ("国外 / International" if lang == "ja" else "International") + "</div>"]
    for y, a, t, v in D.TALKS_INTL:
        out.append("<div class='pub'>" + bold_pi(escape(a)) + " <span class='ti'>" + escape(t) +
                   "</span> " + escape(v) + ", " + escape(str(y)) + ".</div>")
    out.append("<div class='talk-sub'>" + ("国内 / Domestic" if lang == "ja" else "Domestic (Japan)") + "</div>")
    for y, a, t, v in D.TALKS_DOM:
        out.append("<div class='pub'>" + bold_pi(escape(a)) + " <span class='ti'>" + escape(t) +
                   "</span> " + escape(v) + ".</div>")
    return "".join(out)


CONTENT = {
    "ja": {
        "lang": "ja", "title": "略歴 / Curriculum Vitae — 谷英典",
        "meta": "谷英典（横浜薬科大学 准教授, Ph.D.）の詳細略歴。lncRNA・RNA安定性（BRIC-seq開発）。原著49編・総説22編・被引用2,323・h-index 23・外部グラント8件・招待講演19件。",
        "name": "谷 英典", "en_name": "Hidenori Tani, Ph.D.",
        "role": "横浜薬科大学 薬学部 健康薬学科 准教授（2023年〜）",
        "affil": "Department of Health Pharmacy, Faculty of Pharmaceutical Sciences, Yokohama University of Pharmacy",
        "addr": "〒245-0066 神奈川県横浜市戸塚区俣野町601",
        "email_note": "（[at] を @ に置き換えてください）",
        "this": "日本語", "other": "English", "other_href": "cv_en.html", "print": "PDFで保存 / 印刷",
        "L": {"summary": "研究概要", "interests": "研究分野", "appts": "職歴", "edu": "学歴",
              "method": "研究手法・貢献", "selected": "主要業績", "orig": "原著論文",
              "rev_en": "総説（英語）", "rev_jp": "総説（日本語）", "grants": "外部研究費",
              "talks": "招待講演", "teaching": "教育", "service": "査読・学会活動", "books": "一般向け著書"},
        "metrics": [("原著論文", str(N_ORIG)), ("総説", str(N_REV)), ("総被引用", METRICS["citations"]),
                    ("h-index", METRICS["h"]), ("i10-index", METRICS["i10"])],
        "metrics_src": "被引用・h-index・i10-index は Google Scholar（%s 時点）。論文数は研究室業績リストに基づく。" % METRICS["asof"],
        "summary": "専門は分子生物学、特に<b>長鎖ノンコーディングRNA（lncRNA）</b>の機能と代謝。細胞内RNAの安定性（半減期）を網羅的に測定する <b>BRIC-seq 法</b>を開発し、RNA分解を機能の一側面として捉える研究を展開している。近年は単一細胞での RNA turnover、RNA創薬、RNA生物学への計算・AI手法の応用にも取り組む。",
        "interests": ["長鎖ノンコーディングRNA（lncRNA）の機能と代謝",
                      "RNA安定性・半減期のゲノムワイド計測（BRIC-seq）",
                      "転写後制御・RNA分解経路", "化学物質毒性評価のRNAバイオマーカー",
                      "RNA創薬、および RNA生物学への計算・AI手法の応用"],
        "appts": [("2023 –", "<b>准教授</b>　横浜薬科大学 薬学部 健康薬学科", "Associate Professor, Yokohama University of Pharmacy"),
                  ("2012 – 2023", "<b>研究員 → 主任研究員</b>　産業技術総合研究所（AIST）", "Researcher / Senior Researcher, AIST"),
                  ("2009 – 2012", "<b>博士研究員（ポスドク）</b>　東京大学", "Postdoctoral Researcher, University of Tokyo")],
        "edu": [("2008", "<b>博士（工学）</b>　早稲田大学大学院 理工学研究科", "Ph.D. in Engineering, Waseda University"),
                ("", "早稲田大学 理工学部 応用化学科（学部）", "B.Eng., Applied Chemistry, Waseda University")],
        "method": "<b>BRIC-seq（5′-bromo-uridine immunoprecipitation chase sequencing）</b>を開発し、細胞内RNAの安定性（半減期）をゲノムワイドに測定する手法を確立。数百の短寿命ノンコーディング転写産物を同定した（<span class='j'>Genome Research</span>, 2012）。以後、RNA安定性を機能の指標として捉える研究を一貫して展開している。",
        "teaching_head": "横浜薬科大学 担当科目",
        "teaching": ["情報科学入門（1年次・必修）", "情報処理演習（1年次・必修）",
                     "生物系薬学演習1（4年次・必修）", "生物系実習II（2年次・必修／科目責任者）"],
        "service": ["査読：<i>Microbiology and Molecular Biology Reviews</i>（American Society for Microbiology）ほか"],
        "books_line": "一般読者・研究者・大学院生に向けた科学書・実用書を執筆。一覧は <a href='index.html' target='_blank' rel='noopener'>著書ページ</a>。",
        "asof": "As of " + METRICS["asof"],
    },
    "en": {
        "lang": "en", "title": "Curriculum Vitae — Hidenori Tani",
        "meta": "CV of Hidenori Tani, Ph.D. (Associate Professor, Yokohama University of Pharmacy). lncRNA, RNA stability (BRIC-seq). 49 original articles, 22 reviews, 2,323 citations, h-index 23, 8 grants, 19 invited talks.",
        "name": "Hidenori Tani", "en_name": "Ph.D. in Engineering",
        "role": "Associate Professor, Department of Health Pharmacy, Yokohama University of Pharmacy (2023– )",
        "affil": "Faculty of Pharmaceutical Sciences, Yokohama University of Pharmacy",
        "addr": "601 Matano-cho, Totsuka-ku, Yokohama 245-0066, Japan",
        "email_note": "(replace [at] with @)",
        "this": "English", "other": "日本語", "other_href": "cv.html", "print": "Save as PDF / Print",
        "L": {"summary": "Research Summary", "interests": "Research Interests", "appts": "Appointments",
              "edu": "Education", "method": "Method & Contribution", "selected": "Selected Publications",
              "orig": "Original Articles", "rev_en": "Reviews (English)", "rev_jp": "Reviews (Japanese)",
              "grants": "Grants", "talks": "Invited Lectures", "teaching": "Teaching",
              "service": "Service & Peer Review", "books": "Books (General Audience)"},
        "metrics": [("Orig. Articles", str(N_ORIG)), ("Reviews", str(N_REV)), ("Citations", METRICS["citations"]),
                    ("h-index", METRICS["h"]), ("i10-index", METRICS["i10"])],
        "metrics_src": "Citations, h-index and i10-index from Google Scholar (as of %s); article counts from the lab publication list." % METRICS["asof"],
        "summary": "Molecular biologist specializing in <b>long noncoding RNAs (lncRNAs)</b> and their metabolism. Developer of <b>BRIC-seq</b>, a genome-wide method for measuring intracellular RNA stability (half-life), used to study RNA degradation as a facet of function. Current work extends to single-cell RNA turnover, RNA drug development, and computational/AI approaches to RNA biology.",
        "interests": ["Function and metabolism of long noncoding RNAs (lncRNAs)",
                      "Genome-wide measurement of RNA stability / half-life (BRIC-seq)",
                      "Post-transcriptional regulation and RNA degradation pathways",
                      "RNA biomarkers for chemical toxicity assessment",
                      "RNA drug development; computational and AI approaches to RNA biology"],
        "appts": [("2023 –", "<b>Associate Professor</b>, Yokohama University of Pharmacy", "横浜薬科大学 薬学部 健康薬学科"),
                  ("2012 – 2023", "<b>Researcher → Senior Researcher</b>, AIST", "産業技術総合研究所"),
                  ("2009 – 2012", "<b>Postdoctoral Researcher</b>, University of Tokyo", "東京大学")],
        "edu": [("2008", "<b>Ph.D. in Engineering</b>, Waseda University", "早稲田大学大学院 理工学研究科"),
                ("", "B.Eng., Applied Chemistry, Waseda University", "早稲田大学 理工学部 応用化学科")],
        "method": "Developed <b>BRIC-seq (5′-bromo-uridine immunoprecipitation chase sequencing)</b>, establishing genome-wide measurement of intracellular RNA stability (half-life) and identifying hundreds of short-lived noncoding transcripts (<span class='j'>Genome Research</span>, 2012). Subsequent work consistently treats RNA stability as an indicator of function.",
        "teaching_head": "Courses taught, Yokohama University of Pharmacy",
        "teaching": ["Introduction to Information Science (1st year)", "Information Processing Practicum (1st year)",
                     "Biological Pharmacy Seminar I (4th year)", "Biology Laboratory II — immunology (2nd year; course coordinator)"],
        "service": ["Reviewer: <i>Microbiology and Molecular Biology Reviews</i> (American Society for Microbiology), among others"],
        "books_line": "Author of science and practical books for general readers, researchers, and graduate students. See the <a href='en.html' target='_blank' rel='noopener'>books page</a>.",
        "asof": "As of " + METRICS["asof"],
    },
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=Raleway:wght@300;400;500;600&display=swap');
:root{--ink:#000;--ink-soft:#4d4d4d;--ink-mute:#888;--paper:#fff;--accent:#0057E1;--accent-soft:#4a85ea;--line:#e8e6e6;}
*{box-sizing:border-box;}
body{font-family:'Raleway',"Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;color:var(--ink);background:#f4f4f5;margin:0;line-height:1.7;font-size:14px;}
h1,h2,h3{font-family:'Playfair Display',"Hiragino Mincho ProN","Yu Mincho",serif;font-weight:400;}
.toolbar{position:sticky;top:0;z-index:5;background:#f4f4f5;padding:12px 16px;max-width:860px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;}
.lang-nav{font-size:12px;letter-spacing:.06em;}
.lang-nav .active{color:var(--ink);border-bottom:1px solid var(--ink);padding-bottom:2px;margin-right:12px;}
.lang-nav a{color:var(--accent);text-decoration:none;}
.print-btn{font-family:'Raleway',sans-serif;font-size:12px;letter-spacing:.05em;color:#fff;background:var(--accent);border:none;padding:9px 18px;cursor:pointer;}
.print-btn:hover{background:var(--accent-soft);}
.sheet{max-width:860px;margin:0 auto 40px;background:var(--paper);padding:52px 60px 56px;box-shadow:0 4px 24px rgba(0,0,0,.07);}
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
.metric{flex:1;min-width:96px;text-align:center;padding:14px 6px;border-right:1px solid var(--line);}
.metric:last-child{border-right:none;}
.metric .num{font-family:'Playfair Display',serif;font-size:25px;color:var(--accent);line-height:1;}
.metric .lab{font-size:10px;letter-spacing:.08em;color:var(--ink-mute);text-transform:uppercase;margin-top:6px;}
.metric-src{font-size:10.5px;color:var(--ink-mute);text-align:right;margin:4px 0 0;}
section.blk{margin-top:24px;}
.blk h2{font-size:12px;letter-spacing:.2em;color:var(--ink-mute);font-family:'Raleway',sans-serif;font-weight:600;border-bottom:1px solid var(--line);padding-bottom:5px;margin:0 0 12px;text-transform:uppercase;}
.blk h2 .ct{color:var(--ink-mute);font-weight:400;letter-spacing:.05em;}
.row{display:grid;grid-template-columns:112px 1fr;gap:12px;margin-bottom:9px;}
.row .yr{color:var(--ink-mute);font-size:12.5px;}
.row .what b{font-weight:600;}
.row .what .sub{color:var(--ink-mute);font-size:11.5px;}
ul.plain{margin:0;padding-left:17px;}
ul.plain li{margin-bottom:5px;}
.pub{margin-bottom:9px;font-size:12.5px;line-height:1.55;}
.pub b{font-weight:600;}
.pub .ti{}
.pub .j{font-style:italic;color:var(--ink-soft);}
.pub .star{color:var(--accent);margin-right:5px;}
ol.sel{margin:0;padding-left:20px;}
ol.sel li{margin-bottom:9px;font-size:12.5px;line-height:1.55;}
ol.sel li .j{font-style:italic;color:var(--ink-soft);}
ol.sel li b{font-weight:600;}
ol.sel li .star{color:var(--accent);margin-right:4px;}
.talk-sub{font-size:11px;letter-spacing:.1em;color:var(--ink-mute);text-transform:uppercase;margin:10px 0 6px;}
.subhead{font-size:12px;color:var(--ink-soft);margin-bottom:6px;}
.note{font-size:11.5px;color:var(--ink-mute);margin-top:8px;}
.note a,.books a{color:var(--accent);text-decoration:none;}
.asof{color:#bbb;font-size:11px;margin-top:30px;text-align:right;letter-spacing:.05em;}
@media(max-width:600px){.sheet{padding:30px 20px;}.cv-head h1{font-size:28px;}.row{grid-template-columns:84px 1fr;}.metric .num{font-size:20px;}}
@media print{
  @page{size:A4;margin:14mm 13mm;}
  body{background:#fff;font-size:9pt;line-height:1.45;}
  .toolbar{display:none;}
  .sheet{box-shadow:none;max-width:none;margin:0;padding:0;}
  .id-btn{border-color:#999;color:#000;}
  a{color:#000 !important;}
  section.blk{break-inside:avoid;}
  .metrics{break-inside:avoid;}
  .pub,ol.sel li{break-inside:avoid;}
}
"""


def rows(items, lang):
    out = []
    for yr, what, sub in items:
        out.append("<div class='row'><div class='yr'>" + escape(yr) + "</div><div class='what'>" +
                   what + ("<div class='sub'>" + escape(sub) + "</div>" if sub else "") + "</div></div>")
    return "".join(out)


def render(c):
    L = c["L"]

    def h2(key, count=None):
        ct = (" <span class='ct'>(" + str(count) + ")</span>") if count else ""
        return "<h2>" + escape(L[key]) + ct + "</h2>"

    mi = "".join("<div class='metric'><div class='num'>" + escape(v) + "</div><div class='lab'>" +
                 escape(lab) + "</div></div>" for lab, v in c["metrics"])
    metrics = "<div class='metrics'>" + mi + "</div><div class='metric-src'>" + escape(c["metrics_src"]) + "</div>"

    interests = "<ul class='plain'>" + "".join("<li>" + escape(x) + "</li>" for x in c["interests"]) + "</ul>"

    sel_items = [o for n in D.SELECTED_ORIGINALS for o in D.ORIGINALS if o[0] == n]
    sel_items.sort(key=lambda o: (o[1], o[0]), reverse=True)
    selected = pub_ol(sel_items)

    teaching = ("<div class='subhead'>" + escape(c["teaching_head"]) + "</div><ul class='plain'>" +
                "".join("<li>" + escape(x) + "</li>" for x in c["teaching"]) + "</ul>")
    service = "<ul class='plain'>" + "".join("<li>" + x + "</li>" for x in c["service"]) + "</ul>"
    idbtns = "".join("<a class='id-btn' href='" + escape(u) + "'" +
                     (" target='_blank' rel='noopener'" if u.startswith("http") else "") + ">" + escape(t) + "</a>"
                     for t, u in [("ORCID", ORCID_URL), ("Google Scholar", SCHOLAR_URL), ("GitHub", GITHUB_URL),
                                  ("Publications", "publications.html"), ("Data & Code", "software.html")])

    tmpl = """<!DOCTYPE html>
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
  <section class="blk">__H_INT__ __INTERESTS__</section>
  <section class="blk">__H_APPTS__ __APPTS__</section>
  <section class="blk">__H_EDU__ __EDU__</section>
  <section class="blk">__H_METHOD__<div>__METHOD__</div></section>
  <section class="blk">__H_SEL__ __SELECTED__</section>
  <section class="blk">__H_GRANTS__ __GRANTS__</section>
  <section class="blk">__H_TALKS__ __TALKS__</section>
  <section class="blk">__H_TEACH__ __TEACHING__</section>
  <section class="blk">__H_SERVICE__ __SERVICE__</section>
  <section class="blk">__H_BOOKS__ <div class="books">__BOOKS__</div></section>
  <section class="blk">__H_ORIG__ __ORIGINALS__</section>
  <section class="blk">__H_REVEN__ __REVEN__</section>
  <section class="blk">__H_REVJP__ __REVJP__</section>
  <div class="asof">__ASOF__</div>
</div>
</body>
</html>"""
    repl = {
        "__LANG__": c["lang"], "__TITLE__": escape(c["title"]), "__META__": escape(c["meta"]), "__CSS__": CSS,
        "__THIS__": escape(c["this"]), "__OTHER__": escape(c["other"]), "__OTHERHREF__": c["other_href"],
        "__PRINT__": escape(c["print"]), "__NAME__": escape(c["name"]), "__ENNAME__": escape(c["en_name"]),
        "__ROLE__": escape(c["role"]), "__AFFIL__": escape(c["affil"]), "__ADDR__": escape(c["addr"]),
        "__EMAILNOTE__": escape(c["email_note"]), "__ORCIDID__": ORCID, "__IDBTNS__": idbtns, "__METRICS__": metrics,
        "__H_SUMMARY__": h2("summary"), "__SUMMARY__": c["summary"],
        "__H_INT__": h2("interests"), "__INTERESTS__": interests,
        "__H_APPTS__": h2("appts"), "__APPTS__": rows(c["appts"], c["lang"]),
        "__H_EDU__": h2("edu"), "__EDU__": rows(c["edu"], c["lang"]),
        "__H_METHOD__": h2("method"), "__METHOD__": c["method"],
        "__H_SEL__": h2("selected"), "__SELECTED__": selected,
        "__H_GRANTS__": h2("grants", len(D.GRANTS)), "__GRANTS__": grants_rows(c["lang"]),
        "__H_TALKS__": h2("talks", len(D.TALKS_INTL) + len(D.TALKS_DOM)), "__TALKS__": talks_block(c["lang"]),
        "__H_TEACH__": h2("teaching"), "__TEACHING__": teaching,
        "__H_SERVICE__": h2("service"), "__SERVICE__": service,
        "__H_BOOKS__": h2("books"), "__BOOKS__": c["books_line"],
        "__H_ORIG__": h2("orig", N_ORIG), "__ORIGINALS__": originals_by_year(),
        "__H_REVEN__": h2("rev_en", len(D.REVIEWS_EN)), "__REVEN__": reviews_block(D.REVIEWS_EN),
        "__H_REVJP__": h2("rev_jp", len(D.REVIEWS_JP)), "__REVJP__": reviews_block(D.REVIEWS_JP, jp=True),
        "__ASOF__": escape(c["asof"]),
    }
    html = tmpl
    for k, v in repl.items():
        html = html.replace(k, v)
    return html


if __name__ == "__main__":
    for lang, fn in (("ja", "cv.html"), ("en", "cv_en.html")):
        out = os.path.join(HERE, "docs", fn)
        open(out, "w").write(render(CONTENT[lang]))
        print("wrote", out)
    print("originals:", N_ORIG, "reviews:", N_REV, "grants:", len(D.GRANTS),
          "talks:", len(D.TALKS_INTL) + len(D.TALKS_DOM), "selected:", len(D.SELECTED_ORIGINALS))
