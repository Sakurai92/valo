"""
Valorant エージェント当てゲーム — Discord Bot

コマンド一覧:
  !start          ゲーム開始（ランダムなエージェントを選択）
  !ask <質問>     Yes/No質問で絞り込む
  !guess <名前>   エージェント名を予想する
  !status         現在の質問履歴と残り質問数を確認
  !hint           ランダムなヒントを1つもらう
  !agents         全エージェントの一覧を表示
  !giveup         ギブアップして正解を見る
  !help           コマンド一覧を表示

エイリアス:
  !q  → !ask
  !g  → !guess
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from agents import AGENTS, find_agent_by_name, get_display_name
from game_session import GameSession

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ============================================================
# Bot 設定
# ============================================================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,          # デフォルトのhelpを無効化（カスタムhelp使用）
)

# チャンネルIDをキーにゲームセッションを保持
# { channel_id: GameSession }
active_games: dict[int, GameSession] = {}

# ============================================================
# カラー定数
# ============================================================
COLOR_START = 0xFF4655       # Valorant レッド
COLOR_SUCCESS = 0x00C89C     # 正解
COLOR_FAIL = 0xFF6B6B        # 不正解
COLOR_INFO = 0x5865F2        # 情報
COLOR_WARN = 0xFAA61A        # 警告


# ============================================================
# ヘルパー関数
# ============================================================

def get_session(ctx: commands.Context) -> GameSession | None:
    """チャンネルのゲームセッションを取得。なければNone。"""
    return active_games.get(ctx.channel.id)


def require_active_game(ctx: commands.Context) -> GameSession | None:
    """
    アクティブなゲームセッションを取得する。
    ゲームが存在しない場合はNoneを返し、呼び出し元でエラーメッセージを送ること。
    """
    session = get_session(ctx)
    if session is None or not session.is_active:
        return None
    return session


def role_emoji(role: str) -> str:
    return {
        "Controller": "🌫️",
        "Duelist": "⚔️",
        "Sentinel": "🛡️",
        "Initiator": "🔍",
    }.get(role, "❓")


def continent_emoji(continent: str) -> str:
    return {
        "North America": "🌎",
        "South America": "🌎",
        "Europe": "🌍",
        "Asia": "🌏",
        "Africa": "🌍",
        "Oceania": "🌏",
        "Unknown": "❓",
    }.get(continent, "🌐")


def build_status_embed(session: GameSession) -> discord.Embed:
    """ゲーム状況を表示するEmbedを作成する"""
    embed = discord.Embed(
        title="📋 現在のゲーム状況",
        color=COLOR_INFO,
    )
    embed.add_field(
        name="残り質問数",
        value=f"**{session.questions_remaining}** / {session.max_questions}",
        inline=True,
    )
    embed.add_field(
        name="使用済み質問数",
        value=f"**{session.questions_used}**",
        inline=True,
    )

    if session.qa_history:
        embed.add_field(name="\u200b", value="\u200b", inline=False)  # 区切り
        qa_text = ""
        for record in session.qa_history:
            emoji = "✅" if record.answer == "はい" else "❌"
            qa_text += f"{emoji} **Q{record.number}.** {record.question}\n"
        embed.add_field(
            name="質問履歴",
            value=qa_text,
            inline=False,
        )
    else:
        embed.add_field(
            name="質問履歴",
            value="まだ質問がありません。`!ask <質問>` で質問してみよう！",
            inline=False,
        )

    embed.set_footer(text="!ask <質問> で質問 | !guess <名前> で回答 | !hint でヒント")
    return embed


# ============================================================
# イベント
# ============================================================

@bot.event
async def on_ready():
    print(f"Bot起動完了: {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Game(name="Valorant エージェント当てゲーム | !start")
    )


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"引数が足りません。`!help` でコマンド一覧を確認してください。"
        )
    elif isinstance(error, commands.CommandNotFound):
        pass  # 存在しないコマンドは無視
    else:
        raise error


# ============================================================
# コマンド
# ============================================================

@bot.command(name="start")
async def cmd_start(ctx: commands.Context):
    """ゲームを開始する"""
    # 既にゲームが進行中の場合
    existing = get_session(ctx)
    if existing and existing.is_active:
        embed = discord.Embed(
            title="⚠️ ゲームが既に進行中です",
            description=(
                "このチャンネルではすでにゲームが始まっています。\n"
                "`!giveup` でゲームを終了してから新しいゲームを始めてください。"
            ),
            color=COLOR_WARN,
        )
        await ctx.send(embed=embed)
        return

    # 新しいゲームセッションを作成
    session = GameSession()
    active_games[ctx.channel.id] = session

    embed = discord.Embed(
        title="🎮 Valorant エージェント当てゲーム スタート！",
        description=(
            "ランダムなエージェントを1人選びました。\n"
            "質問で絞り込んで、エージェントを当ててください！"
        ),
        color=COLOR_START,
    )
    embed.add_field(
        name="ルール",
        value=(
            f"・最大 **{session.max_questions}** 回まで質問できます\n"
            "・`!ask <質問>` で Yes/No 質問ができます\n"
            "・`!guess <エージェント名>` で答えを予想します\n"
            "・`!hint` でヒントを1つもらえます\n"
            "・`!agents` で全エージェント一覧を確認できます"
        ),
        inline=False,
    )
    embed.add_field(
        name="質問例",
        value=(
            "`!ask 女性ですか？`\n"
            "`!ask デュエリストですか？`\n"
            "`!ask アジア出身ですか？`\n"
            "`!ask スモークを持っていますか？`"
        ),
        inline=False,
    )
    embed.set_footer(text="Good luck! エージェントを当ててみよう！")
    await ctx.send(embed=embed)


@bot.command(name="ask", aliases=["q"])
async def cmd_ask(ctx: commands.Context, *, question: str):
    """エージェントについてYes/No質問をする"""
    session = require_active_game(ctx)
    if session is None:
        await ctx.send(
            "ゲームが始まっていません。`!start` でゲームを開始してください。"
        )
        return

    if session.questions_remaining <= 0:
        await ctx.send(
            "質問回数の上限に達しています。`!guess <名前>` で答えてください！"
        )
        return

    has_remaining, result = session.ask(question)

    if not result.answered:
        embed = discord.Embed(
            title="🤔 質問を理解できませんでした",
            description=(
                "その質問には答えられません。\n"
                "属性に関する質問（ロール・性別・出身地・アビリティなど）を試してください。\n\n"
                "**例:**\n"
                "`!ask 女性ですか？` `!ask デュエリストですか？`\n"
                "`!ask アジア出身ですか？` `!ask フラッシュを持っていますか？`"
            ),
            color=COLOR_WARN,
        )
        await ctx.send(embed=embed)
        return

    # 回答Embedを作成
    is_yes = result.answer == "はい"
    emoji = "✅" if is_yes else "❌"
    color = COLOR_SUCCESS if is_yes else COLOR_FAIL

    embed = discord.Embed(
        title=f"{emoji} {result.answer}",
        color=color,
    )
    embed.add_field(
        name=f"Q{session.questions_used}. {question}",
        value=f"属性: `{result.attribute_label}`",
        inline=False,
    )

    remaining = session.questions_remaining
    if remaining == 0:
        embed.add_field(
            name="⚠️ 残り質問数: 0",
            value="`!guess <エージェント名>` で答えを予想してください！",
            inline=False,
        )
    else:
        embed.set_footer(text=f"残り質問数: {remaining} | !guess <名前> で回答")

    await ctx.send(embed=embed)


@bot.command(name="guess", aliases=["g"])
async def cmd_guess(ctx: commands.Context, *, agent_query: str):
    """エージェント名を予想する"""
    session = require_active_game(ctx)
    if session is None:
        await ctx.send(
            "ゲームが始まっていません。`!start` でゲームを開始してください。"
        )
        return

    # エージェント名を解決（ファジーマッチ）
    matched_name = find_agent_by_name(agent_query)
    if matched_name is None:
        await ctx.send(
            f"「{agent_query}」というエージェントは見つかりませんでした。\n"
            "`!agents` で全エージェント一覧を確認してください。"
        )
        return

    is_correct = session.guess(matched_name)
    guessed_display = get_display_name(matched_name)

    if is_correct:
        # 正解！
        embed = discord.Embed(
            title="🎉 正解！！！",
            description=(
                f"**{guessed_display}（{matched_name}）** で正解です！\n\n"
                f"質問数: **{session.questions_used}** 回"
            ),
            color=COLOR_SUCCESS,
        )
        agent = AGENTS[matched_name]
        embed.add_field(
            name="エージェント情報",
            value=(
                f"{role_emoji(agent['role'])} ロール: **{agent['role']}**\n"
                f"{'👤' if agent['gender'] == 'Male' else '👤'} 性別: **{agent['gender']}**\n"
                f"{continent_emoji(agent['continent'])} 出身: **{agent['country']}**"
            ),
            inline=False,
        )
        if session.qa_history:
            qa_text = ""
            for record in session.qa_history:
                emoji_qa = "✅" if record.answer == "はい" else "❌"
                qa_text += f"{emoji_qa} Q{record.number}. {record.question}\n"
            embed.add_field(name="質問履歴", value=qa_text, inline=False)

        embed.set_footer(text="新しいゲームは !start で始められます")

        # セッションを削除
        active_games.pop(ctx.channel.id, None)
        await ctx.send(embed=embed)

    else:
        # 不正解
        embed = discord.Embed(
            title=f"❌ 不正解... {guessed_display}（{matched_name}）ではありません",
            color=COLOR_FAIL,
        )
        embed.add_field(
            name="残り質問数",
            value=f"**{session.questions_remaining}** 回",
            inline=True,
        )
        embed.set_footer(text="引き続き !ask で質問するか、!guess で再挑戦！")
        await ctx.send(embed=embed)


@bot.command(name="status")
async def cmd_status(ctx: commands.Context):
    """現在のゲーム状況を表示する"""
    session = require_active_game(ctx)
    if session is None:
        await ctx.send(
            "ゲームが始まっていません。`!start` でゲームを開始してください。"
        )
        return

    embed = build_status_embed(session)
    await ctx.send(embed=embed)


@bot.command(name="hint")
async def cmd_hint(ctx: commands.Context):
    """ランダムなヒントを1つ表示する"""
    session = require_active_game(ctx)
    if session is None:
        await ctx.send(
            "ゲームが始まっていません。`!start` でゲームを開始してください。"
        )
        return

    hint_text = session.get_hint()
    embed = discord.Embed(
        title="💡 ヒント",
        description=f"**{hint_text}**",
        color=COLOR_INFO,
    )
    embed.set_footer(text="ヒントは質問回数を消費しません")
    await ctx.send(embed=embed)


@bot.command(name="giveup")
async def cmd_giveup(ctx: commands.Context):
    """ゲームをギブアップして正解を見る"""
    session = require_active_game(ctx)
    if session is None:
        await ctx.send(
            "ゲームが始まっていません。`!start` でゲームを開始してください。"
        )
        return

    agent = session.agent
    answer_name = session.agent_name
    display = session.display_name
    session.give_up()

    embed = discord.Embed(
        title="🏳️ ギブアップ",
        description=f"正解は **{display}（{answer_name}）** でした！",
        color=COLOR_WARN,
    )
    embed.add_field(
        name="エージェント情報",
        value=(
            f"{role_emoji(agent['role'])} ロール: **{agent['role']}**\n"
            f"性別: **{agent['gender']}**\n"
            f"{continent_emoji(agent['continent'])} 出身: **{agent['country']}**"
        ),
        inline=False,
    )
    if session.qa_history:
        qa_text = ""
        for record in session.qa_history:
            emoji_qa = "✅" if record.answer == "はい" else "❌"
            qa_text += f"{emoji_qa} Q{record.number}. {record.question}\n"
        embed.add_field(name="質問履歴", value=qa_text, inline=False)

    embed.set_footer(text="新しいゲームは !start で始められます")

    active_games.pop(ctx.channel.id, None)
    await ctx.send(embed=embed)


@bot.command(name="agents")
async def cmd_agents(ctx: commands.Context):
    """全エージェントの一覧を表示する"""
    # ロール別に分類
    by_role: dict[str, list[str]] = {
        "Duelist": [],
        "Controller": [],
        "Sentinel": [],
        "Initiator": [],
    }
    for name, data in AGENTS.items():
        display = data["display_name"]
        by_role[data["role"]].append(f"{display}（{name}）")

    embed = discord.Embed(
        title="📖 Valorant エージェント一覧",
        description=f"全 **{len(AGENTS)}** エージェント",
        color=COLOR_INFO,
    )
    for role, agent_list in by_role.items():
        embed.add_field(
            name=f"{role_emoji(role)} {role}",
            value="\n".join(agent_list),
            inline=True,
        )
    embed.set_footer(text="!guess <英語名または日本語名> で回答できます")
    await ctx.send(embed=embed)


@bot.command(name="help")
async def cmd_help(ctx: commands.Context):
    """コマンド一覧を表示する"""
    embed = discord.Embed(
        title="🎮 Valorant エージェント当てゲーム — コマンド一覧",
        color=COLOR_INFO,
    )
    commands_info = [
        ("!start", "ゲームを開始する"),
        ("!ask <質問>  / !q <質問>", "Yes/No質問で絞り込む"),
        ("!guess <名前>  / !g <名前>", "エージェント名を予想する"),
        ("!status", "質問履歴と残り質問数を確認"),
        ("!hint", "ランダムなヒントを1つもらう"),
        ("!agents", "全エージェントの一覧を表示"),
        ("!giveup", "ギブアップして正解を見る"),
    ]
    for cmd, desc in commands_info:
        embed.add_field(name=f"`{cmd}`", value=desc, inline=False)

    embed.add_field(
        name="質問できる内容",
        value=(
            "**ロール**: デュエリスト / コントローラー / センチネル / イニシエーター\n"
            "**性別**: 男性 / 女性 / ノンバイナリー\n"
            "**出身**: 国名・地域名（日本、アジア、欧州など）\n"
            "**アビリティ**: スモーク、フラッシュ、回復、壁、索敵、トラップ、タレット、テレポート、デコイ、ペット、ダッシュ、炎・毒"
        ),
        inline=False,
    )
    embed.set_footer(text="Valorant Agent Guessing Game")
    await ctx.send(embed=embed)


# ============================================================
# エントリーポイント
# ============================================================

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError(
            "DISCORD_TOKEN が設定されていません。\n"
            ".env ファイルに DISCORD_TOKEN=<your token> を設定してください。"
        )
    bot.run(TOKEN)
