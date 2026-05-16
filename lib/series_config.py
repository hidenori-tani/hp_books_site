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
    # English series — lang='en' で表示から除外される
    "device-generation-en": {"order": 7, "display_name": "The Device Generation Series", "concept": "", "lang": "en"},
    "ai-research-en": {"order": 8, "display_name": "AI for Researchers Series", "concept": "", "lang": "en"},
    "science-history-en": {"order": 9, "display_name": "Science History (English)", "concept": "", "lang": "en"},
}
