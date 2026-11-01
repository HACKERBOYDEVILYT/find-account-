import os
import re
from dotenv import load_dotenv

load_dotenv()

# ১. এনভায়রনমেন্ট থেকে রিড করা
raw_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
raw_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

# ২. সব ধরনের স্পেস, কোটেশন (" বা '), নতুন লাইন (\n, \r) এবং লুকানো ক্যারেক্টার সম্পূর্ণ মুছে ফেলা
TELEGRAM_BOT_TOKEN = re.sub(r'[\s"\'\r\n]+', '', raw_token)
TELEGRAM_CHAT_ID   = re.sub(r'[\s"\'\r\n]+', '', raw_chat_id)

CHECK_INTERVAL     = int(os.getenv("CHECK_INTERVAL", 300))

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env or GitHub Secrets")
