"""
シリーズ表示設定

- order: 表示順（小さい数字が上）
- display_name: HP上の表示名
- concept: シリーズ説明（1-2行）
- lang: 'jp' or 'en'（'en' は表示から除外）
"""

SERIES_CONFIG = {
    "rna-molecular-biology-jp": {
        "order": 1,
        "display_name": "lncRNA・分子生物学シリーズ",
        "concept": "タンパク質を作らないRNAが拓く新しい医療と生命像。研究現場からの最前線レポート。",
        "lang": "jp",
    },
    "souchi-unyou-sedai-jp": {
        "order": 2,
        "display_name": "装置運用世代シリーズ",
        "concept": "「意志」ではなく「装置」で生きる——HSP研究者がAI時代に編み出した、中年期サバイバル術。",
        "lang": "jp",
    },
    "ai-research-jp": {
        "order": 3,
        "display_name": "AI × 研究シリーズ",
        "concept": "生成AIを「考える相棒」として使うための、研究者発の実践ノウハウ。",
        "lang": "jp",
    },
    "science-history-jp": {
        "order": 4,
        "display_name": "科学史シリーズ",
        "concept": "ノーベル賞の光と影。受賞者と「逃した天才たち」の両側から、科学の発展史を描く。",
        "lang": "jp",
    },
    "researcher-career-jp": {
        "order": 5,
        "display_name": "研究者キャリアシリーズ",
        "concept": "アカデミアで生き残るための、地に足のついた実装ガイド。",
        "lang": "jp",
    },
    "health-molecular-jp": {
        "order": 6,
        "display_name": "健康・分子生物学シリーズ",
        "concept": "薬学部教員が分子レベルで読み解く、日常の健康と美容。",
        "lang": "jp",
    },
    # English series — hp_books_site の英語セクションに表示される
    # The Device Generation は 9 冊あるため 3 サブシリーズに分割
    "device-generation-manifesto-en": {
        "order": 7,
        "display_name": "The Device Generation — Manifesto & Memoir",
        "concept": "The foundational vision behind systems-over-willpower, and the personal stories that shaped it.",
        "lang": "en",
    },
    "device-generation-researcher-en": {
        "order": 8,
        "display_name": "The Device Generation — For Researchers",
        "concept": "Mid-career survival manuals for scientists working at the Wet + Dry + AI intersection.",
        "lang": "en",
    },
    "device-generation-sensitive-en": {
        "order": 9,
        "display_name": "The Device Generation — For Sensitive Thinkers",
        "concept": "Body-brain operating manuals for HSPs navigating midlife, anxiety, and the AI era.",
        "lang": "en",
    },
    "lncrna-rna-therapeutics-en": {
        "order": 10,
        "display_name": "lncRNA & RNA Therapeutics Series",
        "concept": "An accessible guide to the RNA revolution — from hidden genome directives to the mRNA vaccines that ended a pandemic.",
        "lang": "en",
    },
    "ai-research-en": {
        "order": 11,
        "display_name": "AI for Researchers Series",
        "concept": "Practical AI workflows for wet-lab scientists, written by a researcher who turned ChatGPT and Claude into thinking partners.",
        "lang": "en",
    },
    "health-molecular-en": {
        "order": 12,
        "display_name": "Health & Molecular Biology Series",
        "concept": "A pharmacy professor explains the molecular biology behind everyday health — eating, beauty, and aging.",
        "lang": "en",
    },
    "science-history-en": {
        "order": 13,
        "display_name": "Science History Series",
        "concept": "Both sides of the Nobel — the celebrated breakthroughs, and the brilliant discoveries left behind in history's shadow.",
        "lang": "en",
    },
}
