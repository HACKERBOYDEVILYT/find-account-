import asyncio
import logging
from config import CHECK_INTERVAL
from scraper import collect_all
from sender import send, send_startup, send_summary, format_message
from tracker import load_seen, save_seen, make_key

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# GitHub Actions mode: CHECK_INTERVAL=0 → single cycle then exit
SINGLE_CYCLE = CHECK_INTERVAL == 0


async def run():
    seen = load_seen()
    interval_min = CHECK_INTERVAL // 60 if not SINGLE_CYCLE else 5

    if not SINGLE_CYCLE:
        await send_startup(interval_min)

    log.info(f"Mode: {'single-cycle (GitHub Actions)' if SINGLE_CYCLE else 'loop'}")

    while True:
        log.info("Collection cycle starting...")
        results = collect_all()

        new_count = 0
        for item in results:
            key = make_key(item)
            if key not in seen:
                seen.add(key)
                await send(format_message(item))
                await asyncio.sleep(1)
                new_count += 1

        save_seen(seen)
        log.info(f"Cycle done. New: {new_count}")

        await send_summary(new_count, len(seen), interval_min)

        if SINGLE_CYCLE:
            log.info("Single cycle done. Exiting.")
            break

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run())
