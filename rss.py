import os
import sys
import feedparser
from sql import db
from time import sleep, time
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler


if os.path.exists("config.env"):
    load_dotenv("config.env")


try:
    api_id = int(os.environ.get("API_ID"))   # Get it from my.telegram.org
    api_hash = os.environ.get("API_HASH")   # Get it from my.telegram.org
    feed_urls = list(set(i for i in os.environ.get("FEED_URLS").split("|")))  # RSS Feed URL of the site.
    bot_token = os.environ.get("BOT_TOKEN")   # Get it by creating a bot on https://t.me/botfather
    log_channel = int(os.environ.get("LOG_CHANNEL"))   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    check_interval = int(os.environ.get("INTERVAL", 10))   # Check Interval in seconds.  
    max_instances = int(os.environ.get("MAX_INSTANCES", 3))
except Exception as e:
    print(e)
    print("One or more variables missing Re Deva. Exiting !")
    sys.exit(1)


for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")


app = Client(":memory:", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


def create_feed_checker(feed_url):
    def check_feed():
        FEED = feedparser.parse(feed_url)
        entry = FEED.entries[0]
        if entry.id != db.get_link(feed_url).link:
                       # ↓ Edit this message as your needs.
            if "eztv.re" in entry.link:   
                message = f"/mirror {entry.torrent_magneturi} \n\nTitle ⏩ {entry.title} \n\n⚠️ EZTV"
            elif "yts.mx" in entry.link:
                message = f"/mirror {entry.links[1]['href']} \n\nTitle ⏩ {entry.title} \n\n⚠️ YTS"
            elif "rarbg" in entry.link:
                message = f"/mirror {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ RARBG"
            elif "watercache" in entry.link:
                message = f"/mirror {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ TorrentGalaxy"
            elif "limetorrents.pro" in entry.link:
                message = f"/mirror {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ LimeTorrents"
            elif "etorrent.click" in entry.link:
                message = f"/mirror {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ ETorTV"
            elif "x265" in entry.category:
                message = f"/mirror {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ x265Tor"
            else:
                message = f"/mirror {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ ThePirateBay"
            try:
                msg = app.send_message(log_channel, message)
                db.update_link(feed_url, entry.id)
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print( f"Checked RSS FEED: /mirror {entry.link} | {entry.title}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
app.run()
