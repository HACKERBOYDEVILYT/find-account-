import re
import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

ACCOUNT_PATTERN = re.compile(
    r"[\w\.\+\-]+@[\w\-]+\.[\w\.]+"
    r"\s*[:|]\s*"
    r"[\S]{4,}",
    re.IGNORECASE
)

PLATFORM_KEYWORDS = {
    "NETFLIX":     ["netflix", "nflx"],
    "CRUNCHYROLL": ["crunchyroll", "crunchy"],
    "GOOGLE":      ["google", "gmail"],
    "CHATGPT":     ["chatgpt", "openai", "gpt"],
    "CLAUDE":      ["claude", "anthropic"],
}

def detect_platform(text: str) -> str:
    text_lower = text.lower()
    for platform, keywords in PLATFORM_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return platform
    return "GENERAL"


def scrape_bugmenot(platform_domain: str, platform_name: str) -> list[dict]:
    results = []
    url = f"https://bugmenot.com/view/{platform_domain}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for article in soup.find_all("article"):
            username_el = article.find(class_="username")
            password_el = article.find(class_="password")
            if username_el and password_el:
                results.append({
                    "platform": platform_name,
                    "username": username_el.get_text(strip=True),
                    "password": password_el.get_text(strip=True),
                    "source":   "BugMeNot",
                })
    except Exception as e:
        log.error(f"BugMeNot ({platform_domain}): {e}")
    return results


def scrape_reddit(subreddit: str) -> list[dict]:
    results = []
    try:
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
        r = requests.get(
            url,
            headers={**HEADERS, "Accept": "application/json"},
            timeout=10
        )
        if r.status_code != 200:
            return results
        for post in r.json()["data"]["children"]:
            data = post["data"]
            text = data.get("selftext", "") + " " + data.get("title", "")
            for acc in ACCOUNT_PATTERN.findall(text):
                results.append({
                    "platform": detect_platform(text),
                    "account":  acc.strip(),
                    "source":   f"r/{subreddit}",
                    "url":      f"https://reddit.com{data.get('permalink','')}",
                })
    except Exception as e:
        log.error(f"Reddit ({subreddit}): {e}")
    return results


def scrape_telegram_preview(channel_url: str) -> list[dict]:
    results = []
    try:
        r = requests.get(channel_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for msg in soup.find_all("div", class_="tgme_widget_message_text"):
            text = msg.get_text()
            for acc in ACCOUNT_PATTERN.findall(text):
                results.append({
                    "platform": detect_platform(text),
                    "account":  acc.strip(),
                    "source":   channel_url,
                })
    except Exception as e:
        log.error(f"Telegram preview ({channel_url}): {e}")
    return results


def scrape_pastebin(query: str) -> list[dict]:
    results = []
    try:
        r = requests.get(
            f"https://pastebin.com/search?q={query}",
            headers=HEADERS, timeout=10
        )
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", href=re.compile(r"^/[A-Za-z0-9]{8}$"))
        for link in links[:5]:
            paste_url = "https://pastebin.com" + link["href"] + "/raw"
            try:
                pr = requests.get(paste_url, headers=HEADERS, timeout=8)
                for acc in ACCOUNT_PATTERN.findall(pr.text):
                    results.append({
                        "platform": detect_platform(pr.text),
                        "account":  acc.strip(),
                        "source":   paste_url,
                    })
            except:
                pass
    except Exception as e:
        log.error(f"Pastebin ({query}): {e}")
    return results


BUGMENOT_TARGETS = [
    ("netflix.com",          "NETFLIX"),
    ("crunchyroll.com",      "CRUNCHYROLL"),
    ("accounts.google.com",  "GOOGLE"),
    ("chat.openai.com",      "CHATGPT"),
    ("claude.ai",            "CLAUDE"),
]

REDDIT_SUBS = [
    "FreeAccounts",
    "FreeNetflixAccounts",
    "FreeCrunchyroll",
]

TELEGRAM_CHANNELS = [
    "https://t.me/s/free_premium_accounts",
    "https://t.me/s/netflix_free_accounts",
    "https://t.me/s/crunchyroll_accounts_free",
    "https://t.me/s/accounts_free_daily",
    "https://t.me/s/freepremiumtools",
]

PASTEBIN_QUERIES = [
    "netflix+account+free",
    "crunchyroll+free",
    "chatgpt+premium+account",
]


def collect_all() -> list[dict]:
    results = []

    log.info("→ BugMeNot scraping...")
    for domain, name in BUGMENOT_TARGETS:
        results.extend(scrape_bugmenot(domain, name))

    log.info("→ Reddit scraping...")
    for sub in REDDIT_SUBS:
        results.extend(scrape_reddit(sub))

    log.info("→ Telegram channel preview scraping...")
    for ch in TELEGRAM_CHANNELS:
        results.extend(scrape_telegram_preview(ch))

    log.info("→ Pastebin scraping...")
    for q in PASTEBIN_QUERIES:
        results.extend(scrape_pastebin(q))

    log.info(f"Raw results: {len(results)}")
    return results
