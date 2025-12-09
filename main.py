import os 
import logging 
from telegram import Update 
from telegram.ext import Application, CommandHandler, ContextTypes 
from dotenv import load_dotenv 
 
load_dotenv()  # Загружает переменные из .env файла 
 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("Bot works on Railway!") 
 
def main(): 
    if not BOT_TOKEN: 
        logger.error("No BOT_TOKEN in environment variables") 
        print("Current env variables:", dict(os.environ)) 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    logger.info("Starting bot...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
