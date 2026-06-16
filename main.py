from datetime import datetime
import logging
import os
import random
import re
import time
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import InputMediaPhoto, InputMediaVideo
import praw
import prawcore
import tweepy
import wget

# Set up clean logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

def list_to_string(s):
    return " ".join(s)

def process_twitter_update(bot, chat_id, text, consumer_key, consumer_secret, access_token, access_token_secret):
    """Processes an update containing a Twitter link, fetches media, and posts to Telegram."""
    logger.info("Processing Twitter update...")
    
    # Extract tweet ID
    match = re.search(r"twitter\.com/[^/]+/status/(\d+)", text)
    if not match:
        logger.warning("Could not extract tweet ID from update.")
        return False
        
    tweet_id = match.group(1)
    logger.info(f"Extracted Tweet ID: {tweet_id}")

    try:
        # Authenticate with Twitter API (v1.1)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        status = api.get_status(tweet_id, tweet_mode="extended")
    except Exception as e:
        logger.error(f"Failed to fetch tweet status from Twitter API: {e}")
        return False

    # Format text with user mention HTML links
    user_re = re.compile(r"@([A-Za-z0-9_]+)")
    tgml = user_re.sub(
        lambda m: f'<a href="http://twitter.com/{m.group(1)}">{m.group(0)}</a>',
        status.full_text,
    )
    
    created_time = time.strftime("%B %d, %Y %H:%M:%S")
    
    # Strip tweet links out of the Reddit body if it was just the link
    twims = ["https://twitter.com", "twitter.com", "http://twitter.com"]
    if text.strip().startswith(tuple(twims)):
        blog = ""
    else:
        blog = re.sub(r"https://twitter\S+", "", text)
        blog = re.sub(r"https://www.twitter\S+", "", blog)
        blog = re.sub(">", "", blog)
        
    caption = (
        f"{blog.strip()}\n{tgml}\n\n"
        f"— <i>{status.author.name} (<a href='https://twitter.com/{status.author.screen_name}'>@{status.author.screen_name}</a>), "
        f"<a href='https://twitter.com/{status.author.screen_name}/status/{tweet_id}'>{created_time}</a></i>"
    )

    pictures = []
    videos = []
    downloads = []
    tosents = []

    # Extract media from tweet details
    if hasattr(status, "extended_entities") and "media" in status.extended_entities:
        for media_item in status.extended_entities["media"]:
            media_type = media_item.get("type")
            if media_type == "video":
                # Get best video variant
                variants = media_item["video_info"]["variants"]
                mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4"]
                if mp4_variants:
                    mp4_variants.sort(key=lambda x: x.get("bitrate", 0), reverse=True)
                    videos.append(mp4_variants[0]["url"])
            elif media_type == "photo":
                pictures.append(media_item["media_url"])

    try:
        if not videos and not pictures:
            logger.info("Sending text-only tweet description.")
            bot.send_message(chat_id, caption, disable_web_page_preview=True)
            return True

        if len(videos) == 1 and not pictures:
            video_url = videos[0]
            logger.info(f"Sending single video: {video_url}")
            try:
                bot.send_video(chat_id, video_url, caption=caption)
            except Exception as send_err:
                logger.warning(f"Direct video send failed ({send_err}), downloading first...")
                downloaded_file = wget.download(video_url)
                print()
                downloads.append(downloaded_file)
                bot.send_video(chat_id, downloaded_file, caption=caption)
            return True

        if len(pictures) == 1 and not videos:
            photo_url = pictures[0]
            logger.info(f"Sending single photo: {photo_url}")
            try:
                bot.send_photo(chat_id, photo_url, caption=caption)
            except Exception as send_err:
                logger.warning(f"Direct photo send failed ({send_err}), downloading first...")
                downloaded_file = wget.download(photo_url)
                print()
                downloads.append(downloaded_file)
                bot.send_photo(chat_id, downloaded_file, caption=caption)
            return True

        logger.info(f"Processing media group (videos: {len(videos)}, photos: {len(pictures)})...")
        
        for idx, video_url in enumerate(videos):
            downloaded = wget.download(video_url)
            print()
            downloads.append(downloaded)
            media_caption = caption if idx == 0 and not pictures else None
            tosents.append(InputMediaVideo(downloaded, caption=media_caption))

        for idx, photo_url in enumerate(pictures):
            downloaded = wget.download(photo_url)
            print()
            downloads.append(downloaded)
            media_caption = caption if idx == 0 and not videos else None
            tosents.append(InputMediaPhoto(downloaded, caption=media_caption))

        if tosents:
            logger.info(f"Sending media group with {len(tosents)} items.")
            bot.send_media_group(chat_id, media=tosents)

    except Exception as e:
        logger.error(f"Error sending media to Telegram: {e}")
        return False
    finally:
        for f in downloads:
            try:
                if os.path.exists(f):
                    os.remove(f)
                    logger.info(f"Cleaned up download: {f}")
            except Exception as clean_err:
                logger.error(f"Cleanup failed for {f}: {clean_err}")
                
    return True

def run_bot():
    logger.info("Initializing Reddit live to Telegram bot...")
    
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    thread_id = os.environ.get("THREAD_ID")
    chat_id = os.environ.get("CHAT_ID")
    
    if chat_id:
        chat_id = int(chat_id)
        
    if not client_id or not client_secret or not thread_id or not chat_id:
        logger.error("Reddit/Telegram config missing in environment variables.")
        return

    res = random.randint(10000, 99999999999)
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=str(res))
    
    bot = Client(
        api_id=os.environ.get("API_ID"),
        api_hash=os.environ.get("HASH"),
        bot_token=os.environ.get("TOKEN"),
        name=":memory:",
    )
    
    logger.info(f"Streaming updates from Reddit Live Thread: {thread_id}")

    while True:
        try:
            live_thread = reddit.live(thread_id)
            for live_update in live_thread.stream.updates(skip_existing=True):
                try:
                    logger.info(f"New live update: {live_update.body}")
                    bot.start()
                    
                    twims = ["https://twitter.com", "twitter.com", "http://twitter.com"]
                    contains_twitter = any(twim in live_update.body for twim in twims)
                    
                    if contains_twitter:
                        success = process_twitter_update(
                            bot=bot,
                            chat_id=chat_id,
                            text=live_update.body,
                            consumer_key=consumer_key,
                            consumer_secret=consumer_secret,
                            access_token=access_token,
                            access_token_secret=access_token_secret
                        )
                        if not success:
                            bot.send_message(chat_id, live_update.body, disable_web_page_preview=True)
                    else:
                        bot.send_message(chat_id, live_update.body, disable_web_page_preview=True)
                        
                except Exception as update_err:
                    logger.error(f"Error processing update: {update_err}")
                finally:
                    try:
                        bot.stop()
                    except Exception:
                        pass
        except prawcore.exceptions.ServerError as e:
            logger.warning(f"Reddit server error: {e}. Sleeping 60 seconds before reconnecting...")
            time.sleep(60)
        except Exception as e:
            logger.error(f"Unexpected error in live stream: {e}. Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
