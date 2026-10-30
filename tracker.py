import json
from pathlib import Path

SEEN_FILE = "seen_accounts.json"


def load_seen() -> set:
    if Path(SEEN_FILE).exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)


def make_key(item: dict) -> str:
    if "username" in item:
        return f"{item['platform']}:{item['username']}:{item['password']}"
    return f"{item['platform']}:{item.get('account', '')}"
