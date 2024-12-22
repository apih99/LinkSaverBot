import os
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    logger.error("MONGODB_URI not found in environment variables!")
    raise ValueError("MONGODB_URI environment variable is required")

try:
    logger.info("Connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    # Verify connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB!")
    db = client['link_saver_bot']
    links_collection = db['links']
except (ConnectionFailure, ConfigurationError) as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! I\'m Link Saver Bot. I can help you save and organize your links.\n\n'
        'Commands:\n'
        '/save <link> #tag1 #tag2 - Save a link with tags\n'
        '/list - List all your saved links\n'
        '/tags - Show all your used tags\n'
        '/find #tag - Find links by tag'
    )

async def save_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save a link with tags."""
    text = update.message.text.strip()
    if len(text.split()) < 2:
        await update.message.reply_text('Please provide a link and optional tags.\nFormat: /save <link> #tag1 #tag2')
        return

    # Extract link and tags
    parts = text.split()
    link = parts[1]
    tags = [word[1:] for word in parts[2:] if word.startswith('#')]

    # Add https:// if no protocol is specified
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link

    # Validate URL
    try:
        result = urlparse(link)
        if not result.netloc:
            await update.message.reply_text('Please provide a valid URL.\nExample: www.example.com or https://example.com')
            return
    except ValueError:
        await update.message.reply_text('Please provide a valid URL.\nExample: www.example.com or https://example.com')
        return

    # Save to database
    link_data = {
        'user_id': update.effective_user.id,
        'link': link,
        'tags': tags,
        'created_at': datetime.utcnow()
    }
    links_collection.insert_one(link_data)

    await update.message.reply_text(f'Link saved successfully with tags: {", ".join(tags) if tags else "no tags"}')

async def list_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all saved links."""
    user_links = links_collection.find({'user_id': update.effective_user.id})
    message = 'Your saved links:\n\n'
    
    links = list(user_links)
    if not links:
        await update.message.reply_text('You haven\'t saved any links yet.')
        return

    for link in links:
        tags = f' [{", ".join(link["tags"])}]' if link['tags'] else ''
        message += f'• {link["link"]}{tags}\n'

    # Split message if it's too long
    if len(message) > 4000:
        messages = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text(message)

async def show_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all used tags."""
    user_links = links_collection.find({'user_id': update.effective_user.id})
    tags = set()
    for link in user_links:
        tags.update(link.get('tags', []))

    if not tags:
        await update.message.reply_text('You haven\'t used any tags yet.')
        return

    await update.message.reply_text(f'Your tags:\n{", ".join(sorted(tags))}')

async def find_by_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Find links by tag."""
    if not context.args:
        await update.message.reply_text('Please provide a tag to search for.\nFormat: /find #tag')
        return

    tag = context.args[0].replace('#', '')
    links = links_collection.find({
        'user_id': update.effective_user.id,
        'tags': tag
    })

    message = f'Links tagged with #{tag}:\n\n'
    found_links = list(links)
    
    if not found_links:
        await update.message.reply_text(f'No links found with tag #{tag}')
        return

    for link in found_links:
        tags = f' [{", ".join(link["tags"])}]' if link['tags'] else ''
        message += f'• {link["link"]}{tags}\n'

    await update.message.reply_text(message)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('save', save_link))
    application.add_handler(CommandHandler('list', list_links))
    application.add_handler(CommandHandler('tags', show_tags))
    application.add_handler(CommandHandler('find', find_by_tag))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 