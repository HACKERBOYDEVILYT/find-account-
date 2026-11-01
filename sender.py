import logging
import re
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)

# টোকেন এবং চ্যাট আইডি থেকে যেকোনো লুকানো স্পেস বা ইনভ্যালিড ক্যারেক্টার রিমুভ করা হলো
CLEAN_TOKEN = re.sub(r'[^\x20-\x7E]', '', str(TELEGRAM_BOT_TOKEN or '')).strip()
CLEAN_CHAT_ID = re.sub(r'[^\x20-\x7E]', '', str(TELEGRAM_CHAT_ID or '')).strip()

bot = Bot(token=CLEAN_TOKEN)

PLATFORM_EMOJI = {
    "NETFLIX":     "🎬",
    "CRUNCHYROLL": "🍥",
    "GOOGLE":      "🔍",
    "CHATGPT":     "🤖",
    "CLAUDE":      "🧠",
    "GENERAL":     "💎",
}


def format_message(item: dict) -> str:
    emoji    = PLATFORM_EMOJI.get(item.get("platform", "GENERAL"), "🔑")
    platform = item.get("platform", "GENERAL")
    source   = item.get("source", "Unknown")
    now      = datetime.now().strftime("%Y-%m-%d %H:%M")

    if "username" in item and "password" in item:
        account_line = (
            f"👤 `{item['username']}`\n"
            f"🔒 `{item['password']}`"
        )
    else:
        account_line = f"🔑 `{item.get('account', 'N/A')}`"

    msg = (
        f"{emoji} *{platform} — Free Account*\n"
        f"{'─' * 28}\n"
        f"{account_line}\n"
        f"{'─' * 28}\n"
        f"📡 Source: {source}\n"
        f"🕐 {now}\n"
        f"{'─' * 28}\n"
        f"⚡ _EH Munna 👿 Bot_"
    )
    if "url" in item:
        msg += f"\n🔗 [Post]({item['url']})"
    return msg


async def send(message: str):
    try:
        await bot.send_message(
            chat_id=CLEAN_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.error(f"Telegram send error: {e}")


async def send_startup(interval_min: int):
    await bot.send_message(
        chat_id=CLEAN_CHAT_ID,
        text=(
            "🦅 *EH Munna 👿 Account Bot — ONLINE*\n"
            f"⏱ Interval: every `{interval_min}` min\n"
            "🎯 Netflix · Crunchyroll · Google · ChatGPT · Claude\n"
            "📡 BugMeNot · Reddit · Telegram · Pastebin"
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


async def send_summary(new_count: int, total: int, interval_min: int):
    await bot.send_message(
        chat_id=CLEAN_CHAT_ID,
        text=(
            f"📊 *Cycle Done*\n"
            f"✅ New: `{new_count}`\n"
            f"💾 Total tracked: `{total}`\n"
            f"⏳ Next in `{interval_min}` min"
        ),
        parse_mode=ParseMode.MARKDOWN,
    )
