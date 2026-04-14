"""
ゲームセッション管理モジュール

各Discordチャンネルで進行するゲームの状態を管理する。
"""

import random
from dataclasses import dataclass, field
from datetime import datetime

from agents import AGENTS
from question_handler import QuestionResult, answer_question


MAX_QUESTIONS = 20  # 1ゲームで使える最大質問数


@dataclass
class QARecord:
    """1回の質問・回答の記録"""
    number: int            # 何問目か
    question: str          # プレイヤーの質問
    attribute_label: str   # マッチした属性
    answer: str            # "はい" or "いいえ"


class GameSession:
    """
    1チャンネルにつき1つのゲームセッションを管理するクラス。

    使い方:
        session = GameSession()
        result = session.ask("女性ですか？")
        is_correct = session.guess("Jett")
    """

    def __init__(self, max_questions: int = MAX_QUESTIONS):
        # ランダムにエージェントを選択
        self.agent_name: str = random.choice(list(AGENTS.keys()))
        self.agent: dict = AGENTS[self.agent_name]
        self.max_questions: int = max_questions
        self.qa_history: list[QARecord] = []
        self.is_active: bool = True
        self.started_at: datetime = datetime.now()

    @property
    def questions_used(self) -> int:
        """使った質問数"""
        return len(self.qa_history)

    @property
    def questions_remaining(self) -> int:
        """残り質問数"""
        return self.max_questions - self.questions_used

    @property
    def display_name(self) -> str:
        """正解エージェントの日本語表記名"""
        return self.agent["display_name"]

    def ask(self, question: str) -> tuple[bool, QuestionResult]:
        """
        質問を処理する。

        Args:
            question: プレイヤーの質問文

        Returns:
            (has_remaining_questions, QuestionResult)
            has_remaining_questions: まだ質問できるか
            QuestionResult: 質問の解析結果
        """
        if not self.is_active:
            raise RuntimeError("ゲームはすでに終了しています")
        if self.questions_remaining <= 0:
            raise RuntimeError("質問回数の上限に達しています")

        result = answer_question(question, self.agent)

        if result.answered:
            record = QARecord(
                number=self.questions_used + 1,
                question=question,
                attribute_label=result.attribute_label,
                answer=result.answer,
            )
            self.qa_history.append(record)

        has_remaining = self.questions_remaining > 0
        return has_remaining, result

    def guess(self, agent_name: str) -> bool:
        """
        エージェント名を予想する。

        Args:
            agent_name: 英語キー（AGENTS.keys()の要素）

        Returns:
            正解かどうか
        """
        if not self.is_active:
            raise RuntimeError("ゲームはすでに終了しています")

        is_correct = agent_name == self.agent_name
        if is_correct:
            self.is_active = False
        return is_correct

    def give_up(self) -> None:
        """ゲームを終了（ギブアップ）する"""
        self.is_active = False

    def get_hint(self) -> str:
        """
        正解エージェントのランダムな属性ヒントを返す。
        すでに回答済みの属性は除く。
        """
        HINT_ATTRS = [
            ("role", {
                "Controller": "ロール: コントローラー",
                "Duelist": "ロール: デュエリスト",
                "Sentinel": "ロール: センチネル",
                "Initiator": "ロール: イニシエーター",
            }),
            ("gender", {
                "Male": "性別: 男性",
                "Female": "性別: 女性",
                "Non-binary": "性別: ノンバイナリー",
            }),
            ("continent", {
                "North America": "出身地域: 北米",
                "South America": "出身地域: 南米",
                "Europe": "出身地域: ヨーロッパ",
                "Asia": "出身地域: アジア",
                "Africa": "出身地域: アフリカ",
                "Oceania": "出身地域: オセアニア",
                "Unknown": "出身地域: 不明",
            }),
        ]

        bool_hints = [
            ("has_smokes", "スモーク系アビリティを持つ", "スモーク系アビリティを持たない"),
            ("has_flash", "フラッシュアビリティを持つ", "フラッシュアビリティを持たない"),
            ("has_heal", "回復アビリティを持つ", "回復アビリティを持たない"),
            ("has_wall", "壁・バリアアビリティを持つ", "壁・バリアアビリティを持たない"),
            ("has_recon", "索敵・偵察アビリティを持つ", "索敵・偵察アビリティを持たない"),
            ("has_trap", "トラップアビリティを持つ", "トラップアビリティを持たない"),
            ("has_turret", "タレットを持つ", "タレットを持たない"),
            ("has_teleport", "テレポートアビリティを持つ", "テレポートアビリティを持たない"),
            ("has_decoy", "デコイ・囮を作れる", "デコイ・囮を作れない"),
            ("has_pet", "ペット・クリーチャー系アビリティを持つ", "ペット・クリーチャー系アビリティを持たない"),
            ("has_dash", "ダッシュ・高速移動アビリティを持つ", "ダッシュ・高速移動アビリティを持たない"),
        ]

        candidates = []

        for attr, value_map in HINT_ATTRS:
            val = self.agent[attr]
            candidates.append(value_map[val])

        for attr, true_text, false_text in bool_hints:
            val = self.agent[attr]
            candidates.append(true_text if val else false_text)

        return random.choice(candidates)

    def summary_embed_fields(self) -> list[dict]:
        """
        ゲーム状況を Discord Embed のフィールドリストとして返す。
        """
        fields = []
        for record in self.qa_history:
            emoji = "✅" if record.answer == "はい" else "❌"
            fields.append({
                "name": f"Q{record.number}. {record.question}",
                "value": f"{emoji} **{record.answer}**",
                "inline": False,
            })
        return fields
