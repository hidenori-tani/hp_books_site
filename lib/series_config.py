"""
シリーズ表示設定

- order: 表示順（小さい数字が上）
- display_name: HP上の表示名
- concept: シリーズ説明（1-2行）
- lang: 'jp' or 'en'
- cover_class: CSSクラス（cover-* で配色変更）
"""

SERIES_CONFIG = {
    "rna-molecular-biology-jp": {
        "order": 1,
        "display_name": "lncRNA・分子生物学シリーズ",
        "concept": "タンパク質を作らないRNAが拓く新しい医療と生命像。研究現場からの最前線レポート。",
        "lang": "jp",
        "cover_class": "lncrna",
    },
    "souchi-unyou-sedai-jp": {
        "order": 2,
        "display_name": "装置運用世代シリーズ",
        "concept": "「意志」ではなく「装置」で生きる——HSP研究者がAI時代に編み出した、中年期サバイバル術。",
        "lang": "jp",
        "cover_class": "device",
    },
    "ai-research-jp": {
        "order": 3,
        "display_name": "AI × 研究シリーズ",
        "concept": "生成AIを「考える相棒」として使うための、研究者発の実践ノウハウ。",
        "lang": "jp",
        "cover_class": "ai",
    },
    "science-history-jp": {
        "order": 4,
        "display_name": "科学史シリーズ",
        "concept": "ノーベル賞の光と影。受賞者と「逃した天才たち」の両側から、科学の発展史を描く。",
        "lang": "jp",
        "cover_class": "science",
    },
    "researcher-career-jp": {
        "order": 5,
        "display_name": "研究者キャリアシリーズ",
        "concept": "アカデミアで生き残るための、地に足のついた実装ガイド。",
        "lang": "jp",
        "cover_class": "career",
    },
    "health-molecular-jp": {
        "order": 6,
        "display_name": "健康・分子生物学シリーズ",
        "concept": "薬学部教員が分子レベルで読み解く、日常の健康と美容。",
        "lang": "jp",
        "cover_class": "health",
    },
    # English series
    "device-generation-en": {
        "order": 7,
        "display_name": "The Device Generation Series",
        "concept": "Surviving midlife in the age of AI — three books on building life-sustaining apparatus.",
        "lang": "en",
        "cover_class": "en",
    },
    "ai-research-en": {
        "order": 8,
        "display_name": "AI for Researchers Series",
        "concept": "Practical AI techniques from a wet-lab biologist's perspective.",
        "lang": "en",
        "cover_class": "en",
    },
    "science-history-en": {
        "order": 9,
        "display_name": "Science History (English)",
        "concept": "Stories of brilliant discoverers history left behind.",
        "lang": "en",
        "cover_class": "en",
    },
}

# 未シリーズ化の英語本（standalone セクションに配置）
STANDALONE_SECTION = {
    "order": 10,
    "display_name": "Standalone English Titles",
    "concept": "Independent works awaiting series integration.",
    "lang": "en",
    "cover_class": "en",
}

# Paperback ASIN マッピング（暫定ハードコード）
# 将来的には books/<slug>.md の YAML に paperback_asin: フィールドを追加して移行
PAPERBACK_MAP = {
    # 装置運用世代シリーズ3冊（推定。実ASIN取得後に上書き）
    "B0GZJF83SV": None,  # 心の中の評議会 ペーパーバック ISBN 9798196015403（KDP差戻し対応中）
    "B0GZCPDL6V": None,  # AI時代の脳疲労マネジメント
    "B0GX5L2GC2": None,  # 就職氷河期世代の生き延び方
}
