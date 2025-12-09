import os 
import logging 
from telegram import Update 
from telegram.ext import Application, CommandHandler, ContextTypes 
from dotenv import load_dotenv 
 
load_dotenv() 
 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("Bot works on Railway!") 
 
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("Commands: /start, /help, /status") 
 
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("Bot is running on Railway!") 
 
def main(): 
    if not BOT_TOKEN: 
        logger.error("No BOT_TOKEN") 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CommandHandler("help", help_command)) 
    app.add_handler(CommandHandler("status", status)) 
    logger.info("Starting bot...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
