# Telegram Link Saver Bot

A Telegram bot that helps you save and organize links with tags. Perfect for keeping track of useful articles, websites, and videos.

## Features

- Save links with custom tags
- List all saved links
- View all used tags
- Search links by tag
- Supports long messages by splitting them automatically

## Setup

1. Create a new bot with [@BotFather](https://t.me/botfather) on Telegram and get your bot token
2. Create a MongoDB database (you can use MongoDB Atlas for free)
3. Set up environment variables:

Create a `.env` file with:
```
TELEGRAM_TOKEN=your_telegram_bot_token
MONGODB_URI=your_mongodb_connection_string
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the bot:
```bash
python bot.py
```

## Deployment on Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add the following environment variables in Railway:
   - `TELEGRAM_TOKEN`
   - `MONGODB_URI`
4. Deploy the project

Railway will automatically detect the Dockerfile and deploy your bot.

## Usage

- `/start` - Get started with the bot
- `/save <link> #tag1 #tag2` - Save a link with optional tags
- `/list` - List all your saved links
- `/tags` - Show all your used tags
- `/find #tag` - Find links by tag

## Example

```
/save https://example.com #article #tech
/save https://another-example.com #video #tutorial
/find #tech
``` 