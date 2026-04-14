"""
質問解析・回答モジュール

プレイヤーが入力した自然言語の質問を解析し、
エージェントの属性に基づいてYes/Noで回答する。
日本語・英語の両方の質問に対応。
"""

from dataclasses import dataclass


@dataclass
class QuestionResult:
    answered: bool          # 質問を解析できたか
    answer: str             # "はい" / "いいえ"
    attribute_label: str    # 回答に使った属性の説明


# ============================================================
# パターン定義
# 各パターンは「attr（エージェントdictのキー）」か
# 「カスタムロジック（custom_check）」を持つ
# ============================================================

PATTERNS: list[dict] = [
    # ---------- ロール ----------
    {
        "label": "ロール（デュエリスト）",
        "keywords": ["デュエリスト", "duelist"],
        "check": lambda a: a["role"] == "Duelist",
    },
    {
        "label": "ロール（コントローラー）",
        "keywords": ["コントローラー", "controller"],
        "check": lambda a: a["role"] == "Controller",
    },
    {
        "label": "ロール（センチネル）",
        "keywords": ["センチネル", "sentinel"],
        "check": lambda a: a["role"] == "Sentinel",
    },
    {
        "label": "ロール（イニシエーター）",
        "keywords": ["イニシエーター", "イニシ", "initiator"],
        "check": lambda a: a["role"] == "Initiator",
    },
    # ---------- 性別 ----------
    {
        "label": "性別（女性）",
        "keywords": ["女性", "女", "女の子", "female", "woman", "girl", "彼女"],
        "check": lambda a: a["gender"] == "Female",
    },
    {
        "label": "性別（男性）",
        "keywords": ["男性", "男", "男の子", "male", "man", "boy", "彼"],
        "check": lambda a: a["gender"] == "Male",
    },
    {
        "label": "性別（ノンバイナリー）",
        "keywords": ["ノンバイナリー", "non-binary", "nonbinary", "nb", "ノンバ"],
        "check": lambda a: a["gender"] == "Non-binary",
    },
    # ---------- 人間かどうか ----------
    {
        "label": "人間かどうか",
        "keywords": ["人間", "ヒューマン", "human", "生身", "生物", "人"],
        "exclude_keywords": ["非人間", "not human"],
        "check": lambda a: a["human"],
    },
    {
        "label": "ロボット・AI・人外",
        "keywords": ["ロボット", "ロボ", "robot", "ai", "機械", "人工知能", "android", "人外", "非人間"],
        "check": lambda a: not a["human"],
    },
    # ---------- 大陸・地域 ----------
    {
        "label": "出身地域（アジア）",
        "keywords": ["アジア", "asia", "アジア出身", "東アジア", "アジア系"],
        "check": lambda a: a["continent"] == "Asia",
    },
    {
        "label": "出身地域（ヨーロッパ）",
        "keywords": ["ヨーロッパ", "europe", "欧州", "ヨーロッパ出身", "欧米"],
        "check": lambda a: a["continent"] == "Europe",
    },
    {
        "label": "出身地域（北米）",
        "keywords": ["北米", "north america", "北アメリカ", "アメリカ大陸北部"],
        "check": lambda a: a["continent"] == "North America",
    },
    {
        "label": "出身地域（南米）",
        "keywords": ["南米", "south america", "南アメリカ", "ラテンアメリカ", "中南米"],
        "check": lambda a: a["continent"] == "South America",
    },
    {
        "label": "出身地域（アフリカ）",
        "keywords": ["アフリカ", "africa"],
        "check": lambda a: a["continent"] == "Africa",
    },
    {
        "label": "出身地域（オセアニア）",
        "keywords": ["オセアニア", "oceania", "オーストラリア大陸"],
        "check": lambda a: a["continent"] == "Oceania",
    },
    {
        "label": "出身地域（不明）",
        "keywords": ["出身不明", "謎の出身", "unknown origin"],
        "check": lambda a: a["continent"] == "Unknown",
    },
    # ---------- 国籍 ----------
    {
        "label": "出身国（アメリカ）",
        "keywords": ["アメリカ", "usa", "us", "米国", "アメリカ合衆国", "america"],
        "exclude_keywords": ["南米", "ラテンアメリカ", "中南米"],
        "check": lambda a: a["country"] == "アメリカ",
    },
    {
        "label": "出身国（イギリス）",
        "keywords": ["イギリス", "uk", "英国", "britain", "england", "british"],
        "check": lambda a: a["country"] == "イギリス",
    },
    {
        "label": "出身国（韓国）",
        "keywords": ["韓国", "south korea", "korea", "コリア", "korean"],
        "check": lambda a: a["country"] == "韓国",
    },
    {
        "label": "出身国（日本）",
        "keywords": ["日本", "japan", "japanese"],
        "check": lambda a: a["country"] == "日本",
    },
    {
        "label": "出身国（ブラジル）",
        "keywords": ["ブラジル", "brazil", "brazilian"],
        "check": lambda a: a["country"] == "ブラジル",
    },
    {
        "label": "出身国（中国）",
        "keywords": ["中国", "china", "chinese"],
        "check": lambda a: a["country"] == "中国",
    },
    {
        "label": "出身国（メキシコ）",
        "keywords": ["メキシコ", "mexico", "mexican"],
        "check": lambda a: a["country"] == "メキシコ",
    },
    {
        "label": "出身国（ドイツ）",
        "keywords": ["ドイツ", "germany", "german"],
        "check": lambda a: a["country"] == "ドイツ",
    },
    {
        "label": "出身国（モロッコ）",
        "keywords": ["モロッコ", "morocco", "moroccan"],
        "check": lambda a: a["country"] == "モロッコ",
    },
    {
        "label": "出身国（ロシア）",
        "keywords": ["ロシア", "russia", "russian"],
        "check": lambda a: a["country"] == "ロシア",
    },
    {
        "label": "出身国（スウェーデン）",
        "keywords": ["スウェーデン", "sweden", "swedish"],
        "check": lambda a: a["country"] == "スウェーデン",
    },
    {
        "label": "出身国（オーストラリア）",
        "keywords": ["オーストラリア", "australia", "australian"],
        "check": lambda a: a["country"] == "オーストラリア",
    },
    {
        "label": "出身国（フランス）",
        "keywords": ["フランス", "france", "french"],
        "check": lambda a: a["country"] == "フランス",
    },
    {
        "label": "出身国（フィリピン）",
        "keywords": ["フィリピン", "philippines", "filipino", "filipina"],
        "check": lambda a: a["country"] == "フィリピン",
    },
    {
        "label": "出身国（トルコ）",
        "keywords": ["トルコ", "turkey", "turkish"],
        "check": lambda a: a["country"] == "トルコ",
    },
    {
        "label": "出身国（ガーナ）",
        "keywords": ["ガーナ", "ghana", "ghanaian"],
        "check": lambda a: a["country"] == "ガーナ",
    },
    {
        "label": "出身国（インド）",
        "keywords": ["インド", "india", "indian"],
        "check": lambda a: a["country"] == "インド",
    },
    {
        "label": "出身国（ノルウェー）",
        "keywords": ["ノルウェー", "norway", "norwegian"],
        "check": lambda a: a["country"] == "ノルウェー",
    },
    {
        "label": "出身国（コロンビア）",
        "keywords": ["コロンビア", "colombia", "colombian"],
        "check": lambda a: a["country"] == "コロンビア",
    },
    {
        "label": "出身国（スコットランド）",
        "keywords": ["スコットランド", "scotland", "scottish"],
        "check": lambda a: a["country"] == "スコットランド",
    },
    # ---------- アビリティ系 ----------
    {
        "label": "スモーク（視界遮断）アビリティ",
        "keywords": [
            "スモーク", "smoke", "煙幕", "煙", "霧",
            "スモークを持つ", "スモークを使える", "視界遮断",
        ],
        "check": lambda a: a["has_smokes"],
    },
    {
        "label": "フラッシュアビリティ",
        "keywords": [
            "フラッシュ", "flash", "閃光", "フラシュ", "目つぶし", "目くらまし",
            "フラッシュを持つ", "フラッシュを使える",
        ],
        "check": lambda a: a["has_flash"],
    },
    {
        "label": "回復アビリティ",
        "keywords": [
            "回復", "ヒール", "heal", "healing", "治療", "リジェネ",
            "治せる", "回復できる", "ヒールを持つ",
        ],
        "check": lambda a: a["has_heal"],
    },
    {
        "label": "壁・バリアアビリティ",
        "keywords": [
            "壁", "バリア", "wall", "barrier", "遮蔽物",
            "壁を作れる", "バリアを張れる",
        ],
        "check": lambda a: a["has_wall"],
    },
    {
        "label": "索敵・偵察アビリティ",
        "keywords": [
            "索敵", "偵察", "スキャン", "recon", "scan", "reveal",
            "敵の位置", "マップ", "見える", "暴く",
        ],
        "check": lambda a: a["has_recon"],
    },
    {
        "label": "トラップアビリティ",
        "keywords": [
            "トラップ", "罠", "trap", "tripwire", "地雷",
            "ワイヤー", "wire",
        ],
        "check": lambda a: a["has_trap"],
    },
    {
        "label": "タレット（自動砲台）アビリティ",
        "keywords": [
            "タレット", "砲台", "turret", "自動砲台", "銃座",
        ],
        "check": lambda a: a["has_turret"],
    },
    {
        "label": "テレポートアビリティ",
        "keywords": [
            "テレポート", "teleport", "瞬間移動", "TP", "転送",
        ],
        "check": lambda a: a["has_teleport"],
    },
    {
        "label": "デコイ・囮アビリティ",
        "keywords": [
            "デコイ", "囮", "decoy", "fake", "フェイク", "分身",
        ],
        "check": lambda a: a["has_decoy"],
    },
    {
        "label": "ペット・クリーチャー系アビリティ",
        "keywords": [
            "ペット", "動物", "pet", "animal", "生き物", "クリーチャー",
            "companion", "仲間", "生物", "creature",
        ],
        "check": lambda a: a["has_pet"],
    },
    {
        "label": "ダッシュ・高速移動アビリティ",
        "keywords": [
            "ダッシュ", "dash", "瞬足", "sprint", "高速移動",
            "速い", "スプリント",
        ],
        "check": lambda a: a["has_dash"],
    },
    {
        "label": "炎・毒系AOEダメージアビリティ",
        "keywords": [
            "炎", "火", "毒", "poison", "molotov", "incendiary",
            "燃焼", "焼く", "火炎", "火の玉", "火の壁", "毒ゾーン",
        ],
        "check": lambda a: a["has_molotov"],
    },
]


def answer_question(question: str, agent: dict) -> QuestionResult:
    """
    プレイヤーの質問を解析し、エージェントの属性に基づいて回答する。

    Args:
        question: プレイヤーが入力した質問文
        agent: agents.pyのAGENTS[name]に対応するdict

    Returns:
        QuestionResult
    """
    q = question.lower().strip()

    for pattern in PATTERNS:
        keywords = pattern["keywords"]
        exclude_keywords = pattern.get("exclude_keywords", [])

        # 除外キーワードが含まれていたらスキップ
        if any(ex in q for ex in exclude_keywords):
            continue

        # マッチチェック
        if any(kw.lower() in q for kw in keywords):
            result = pattern["check"](agent)
            return QuestionResult(
                answered=True,
                answer="はい" if result else "いいえ",
                attribute_label=pattern["label"],
            )

    # どのパターンにも一致しなかった
    return QuestionResult(
        answered=False,
        answer="",
        attribute_label="",
    )


def filter_agents_by_answers(
    agents: dict,
    qa_history: list[tuple[str, str, str]],
) -> list[str]:
    """
    これまでの質問・回答履歴を元に、まだ可能性があるエージェント名のリストを返す。

    Args:
        agents: AGENTSのdict全体
        qa_history: (質問, attribute_label, answer) のリスト

    Returns:
        まだ候補として残っているエージェント名のリスト
    """
    remaining = list(agents.keys())

    for question, attribute_label, answer in qa_history:
        still_remaining = []
        for name in remaining:
            result = answer_question(question, agents[name])
            if result.answered and result.answer == answer:
                still_remaining.append(name)
        remaining = still_remaining

    return remaining
