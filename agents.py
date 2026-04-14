"""
Valorant エージェントデータ

属性一覧:
- role: Controller / Duelist / Sentinel / Initiator
- gender: Male / Female / Non-binary
- country: 出身国（日本語表記）
- continent: North America / South America / Europe / Asia / Africa / Oceania / Unknown
- human: 人間かどうか（False = KAYO、Omen など）
- has_smokes: 視界を遮るスモーク系アビリティを持つ
- has_flash: 閃光（フラッシュ）アビリティを持つ
- has_heal: 回復アビリティを持つ
- has_wall: 壁・バリアを展開できる
- has_recon: 敵の位置を索敵・開示できる
- has_trap: トラップを設置できる
- has_turret: 自動砲台（タレット）を持つ
- has_teleport: テレポートできる
- has_decoy: デコイ・囮を作れる
- has_pet: 動物・クリーチャーの仲間を操る
- has_dash: 高速移動・ダッシュ系アビリティを持つ
- has_molotov: 炎・毒などのAOEダメージゾーンを生成する
"""

AGENTS: dict[str, dict] = {
    # ========== DUELISTS ==========
    "Phoenix": {
        "display_name": "フェニックス",
        "role": "Duelist",
        "gender": "Male",
        "country": "イギリス",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Curveball
        "has_heal": True,        # Hot Hands（炎で自己回復）、Run it Back（完全復活）
        "has_wall": True,        # Blaze（炎の壁）
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": True,     # Hot Hands
    },
    "Reyna": {
        "display_name": "レイナ",
        "role": "Duelist",
        "gender": "Female",
        "country": "メキシコ",
        "continent": "North America",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Leer（目玉フラッシュ）
        "has_heal": True,        # Devour（魂を食って回復）
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": True,        # Dismiss（無敵フェーズ移動）
        "has_molotov": False,
    },
    "Jett": {
        "display_name": "ジェット",
        "role": "Duelist",
        "gender": "Female",
        "country": "韓国",
        "continent": "Asia",
        "human": True,
        "has_smokes": True,      # Cloudburst
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": True,        # Tailwind
        "has_molotov": False,
    },
    "Raze": {
        "display_name": "レイズ",
        "role": "Duelist",
        "gender": "Female",
        "country": "ブラジル",
        "continent": "South America",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": True,         # Boom Bot（ロボ）
        "has_dash": True,        # Blast Pack
        "has_molotov": False,
    },
    "Yoru": {
        "display_name": "ヨル",
        "role": "Duelist",
        "gender": "Male",
        "country": "日本",
        "continent": "Asia",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Fakeout（音デコイ→フラッシュ）
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": True,    # Gatecrash
        "has_decoy": True,       # Fakeout（フェイクの足音デコイ）
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Neon": {
        "display_name": "ネオン",
        "role": "Duelist",
        "gender": "Female",
        "country": "フィリピン",
        "continent": "Asia",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": True,        # Fast Lane（電気の壁）
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": True,        # High Gear（超高速スプリント）
        "has_molotov": False,
    },
    "Iso": {
        "display_name": "イソ",
        "role": "Duelist",
        "gender": "Male",
        "country": "中国",
        "continent": "Asia",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Waylay": {
        "display_name": "ウェイレイ",
        "role": "Duelist",
        "gender": "Female",
        "country": "韓国",
        "continent": "Asia",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # 光系フラッシュ
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": True,        # 高速移動
        "has_molotov": False,
    },
    # ========== CONTROLLERS ==========
    "Brimstone": {
        "display_name": "ブリムストーン",
        "role": "Controller",
        "gender": "Male",
        "country": "アメリカ",
        "continent": "North America",
        "human": True,
        "has_smokes": True,      # Sky Smoke
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": True,     # Incendiary
    },
    "Viper": {
        "display_name": "バイパー",
        "role": "Controller",
        "gender": "Female",
        "country": "アメリカ",
        "continent": "North America",
        "human": True,
        "has_smokes": True,      # Poison Cloud
        "has_flash": False,
        "has_heal": False,
        "has_wall": True,        # Toxic Screen
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": True,     # Snake Bite
    },
    "Omen": {
        "display_name": "オーメン",
        "role": "Controller",
        "gender": "Male",
        "country": "不明",
        "continent": "Unknown",
        "human": False,          # 謎の存在（元人間から変容した霊的存在）
        "has_smokes": True,      # Dark Cover
        "has_flash": True,       # Paranoia
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": True,    # Shrouded Step / From the Shadows
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Astra": {
        "display_name": "アストラ",
        "role": "Controller",
        "gender": "Female",
        "country": "ガーナ",
        "continent": "Africa",
        "human": True,
        "has_smokes": True,      # Nebula
        "has_flash": False,
        "has_heal": False,
        "has_wall": True,        # Cosmic Divide（アルト：巨大な壁）
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Harbor": {
        "display_name": "ハーバー",
        "role": "Controller",
        "gender": "Male",
        "country": "インド",
        "continent": "Asia",
        "human": True,
        "has_smokes": True,      # High Tide / Cove
        "has_flash": False,
        "has_heal": False,
        "has_wall": True,        # High Tide（水の壁）
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Clove": {
        "display_name": "クローブ",
        "role": "Controller",
        "gender": "Non-binary",
        "country": "スコットランド",
        "continent": "Europe",
        "human": True,
        "has_smokes": True,
        "has_flash": False,
        "has_heal": True,        # Pick-Me-Up（キル後に回復）
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    # ========== SENTINELS ==========
    "Sage": {
        "display_name": "セージ",
        "role": "Sentinel",
        "gender": "Female",
        "country": "中国",
        "continent": "Asia",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": True,        # Healing Orb / Resurrection（蘇生）
        "has_wall": True,        # Barrier Orb
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Cypher": {
        "display_name": "サイファー",
        "role": "Sentinel",
        "gender": "Male",
        "country": "モロッコ",
        "continent": "Africa",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": True,       # Spycam / Neural Theft
        "has_trap": True,        # Trapwire / Cyber Cage
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Killjoy": {
        "display_name": "キルジョイ",
        "role": "Sentinel",
        "gender": "Female",
        "country": "ドイツ",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": True,       # Alarmbot（敵を検知してタグ付け）
        "has_trap": True,        # Alarmbot / Nanoswarm
        "has_turret": True,      # Turret
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Chamber": {
        "display_name": "チェンバー",
        "role": "Sentinel",
        "gender": "Male",
        "country": "フランス",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": True,        # Trademark（近接トリップワイヤー）
        "has_turret": False,
        "has_teleport": True,    # Rendezvous
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Deadlock": {
        "display_name": "デッドロック",
        "role": "Sentinel",
        "gender": "Female",
        "country": "ノルウェー",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": True,        # Gravenet / Sonic Sensor
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Vyse": {
        "display_name": "ヴァイス",
        "role": "Sentinel",
        "gender": "Female",
        "country": "不明",
        "continent": "Unknown",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Arc Rose（フラッシュ効果）
        "has_heal": False,
        "has_wall": True,        # Shear（地面から壁）
        "has_recon": False,
        "has_trap": True,        # Razorvine / Arc Rose
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    # ========== INITIATORS ==========
    "Sova": {
        "display_name": "ソーヴァ",
        "role": "Initiator",
        "gender": "Male",
        "country": "ロシア",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": True,       # Recon Bolt / Owl Drone
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": True,         # Owl Drone（ドローン操作）
        "has_dash": False,
        "has_molotov": False,
    },
    "Breach": {
        "display_name": "ブリーチ",
        "role": "Initiator",
        "gender": "Male",
        "country": "スウェーデン",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Flashpoint
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Skye": {
        "display_name": "スカイ",
        "role": "Initiator",
        "gender": "Female",
        "country": "オーストラリア",
        "continent": "Oceania",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Guiding Light（鳥フラッシュ）
        "has_heal": True,        # Regrowth
        "has_wall": False,
        "has_recon": True,       # Trailblazer / Seekers
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": True,         # Trailblazer（狼）、Guiding Light（鳥）
        "has_dash": False,
        "has_molotov": False,
    },
    "KAYO": {
        "display_name": "ケイオー",
        "role": "Initiator",
        "gender": "Male",
        "country": "不明",
        "continent": "Unknown",
        "human": False,          # 戦闘ロボット
        "has_smokes": False,
        "has_flash": True,       # FLASH/drive
        "has_heal": False,
        "has_wall": False,
        "has_recon": False,
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": False,
        "has_dash": False,
        "has_molotov": False,
    },
    "Fade": {
        "display_name": "フェイド",
        "role": "Initiator",
        "gender": "Female",
        "country": "トルコ",
        "continent": "Europe",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": True,       # Haunt / Prowler / Nightfall
        "has_trap": True,        # Seize（敵を拘束）
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": True,         # Prowler（クリーチャー）
        "has_dash": False,
        "has_molotov": False,
    },
    "Gekko": {
        "display_name": "ゲッコー",
        "role": "Initiator",
        "gender": "Male",
        "country": "アメリカ",
        "continent": "North America",
        "human": True,
        "has_smokes": False,
        "has_flash": True,       # Dizzy（ゴーフラッシュ）
        "has_heal": False,
        "has_wall": False,
        "has_recon": True,       # Thrash（ルームクリア）
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": True,         # Dizzy, Wingman, Thrash, Mosh
        "has_dash": False,
        "has_molotov": False,
    },
    "Tejo": {
        "display_name": "テホ",
        "role": "Initiator",
        "gender": "Male",
        "country": "コロンビア",
        "continent": "South America",
        "human": True,
        "has_smokes": False,
        "has_flash": False,
        "has_heal": False,
        "has_wall": False,
        "has_recon": True,       # Stealth Drone
        "has_trap": False,
        "has_turret": False,
        "has_teleport": False,
        "has_decoy": False,
        "has_pet": True,         # Stealth Drone
        "has_dash": False,
        "has_molotov": False,
    },
}


def get_all_names() -> list[str]:
    """全エージェントの英語名一覧を返す"""
    return list(AGENTS.keys())


def get_display_name(name: str) -> str:
    """英語名から日本語表記名を返す"""
    return AGENTS[name]["display_name"]


def get_all_display_names() -> list[str]:
    """全エージェントの日本語表記名一覧を返す"""
    return [data["display_name"] for data in AGENTS.values()]


def find_agent_by_name(query: str) -> str | None:
    """
    クエリ文字列からエージェント名（英語キー）を検索する。
    英語名・日本語名どちらも対応。見つからなければNoneを返す。
    """
    import difflib

    query_lower = query.lower().strip()

    # 完全一致（英語・大文字小文字無視）
    for name in AGENTS:
        if name.lower() == query_lower:
            return name

    # 日本語名での完全一致
    for name, data in AGENTS.items():
        if data["display_name"] == query.strip():
            return name

    # 英語名でのファジーマッチ
    en_names = list(AGENTS.keys())
    matches = difflib.get_close_matches(query, en_names, n=1, cutoff=0.6)
    if matches:
        return matches[0]

    # 日本語名でのファジーマッチ
    ja_names = [data["display_name"] for data in AGENTS.values()]
    ja_matches = difflib.get_close_matches(query, ja_names, n=1, cutoff=0.6)
    if ja_matches:
        for name, data in AGENTS.items():
            if data["display_name"] == ja_matches[0]:
                return name

    # 部分一致（英語）
    for name in AGENTS:
        if query_lower in name.lower():
            return name

    # 部分一致（日本語）
    for name, data in AGENTS.items():
        if query.strip() in data["display_name"]:
            return name

    return None
