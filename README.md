# reddit-live-to-telegram

A Python bot that streams a **Reddit live thread** and mirrors its updates to a
**Telegram chat/channel**. When an update contains a Twitter/X link, it fetches
the tweet (text + photos/videos) via the Twitter API and forwards the media to
Telegram with a formatted caption; other updates are forwarded as plain messages.

> ⚠️ Educational / hobby project. Use responsibly and in line with Reddit's,
> Twitter/X's, and Telegram's Terms of Service.

## How it works

1. Streams updates from a Reddit live thread via [PRAW](https://praw.readthedocs.io/).
2. For tweet links, pulls the status with [Tweepy](https://www.tweepy.org/) and
   builds an HTML caption with author attribution.
3. Downloads any attached media and sends it to Telegram via
   [Pyrogram](https://docs.pyrogram.org/) (single media or media group).
4. Plain updates are relayed as text messages.

## Requirements

- Python 3.x
- The packages in [`requirements.txt`](./requirements.txt)

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example env file and fill in your own values:

```bash
cp .env.example .env
# edit .env
```

| Variable | Description |
|----------|-------------|
| `API_ID` | Telegram API id (https://my.telegram.org) |
| `HASH` | Telegram API hash |
| `TOKEN` | Telegram bot token (from @BotFather) |
| `CHAT_ID` | Target Telegram chat/channel id |
| `THREAD_ID` | Reddit live thread id |
| `CLIENT_ID` | Reddit app client id |
| `CLIENT_SECRET` | Reddit app client secret |
| `TWITTER_CONSUMER_KEY` | Twitter/X API consumer key |
| `TWITTER_CONSUMER_SECRET` | Twitter/X API consumer secret |
| `TWITTER_ACCESS_TOKEN` | Twitter/X access token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter/X access token secret |

## Running

```bash
python main.py
```

## License

[MIT](./LICENSE)
