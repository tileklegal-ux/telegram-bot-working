import os 
import logging 
from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [ 
        ["ANALYZE PRODUCT", "PROFILE NICHE"], 
        ["CALCULATE MARGIN", "HELP"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("ARTBAZAR AI ready! Choose:", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    # Игнорируем текст кнопок 
    user_text = update.message.text 
    if user_text in ["ANALYZE PRODUCT", "PROFILE NICHE", "CALCULATE MARGIN", "HELP"]: 
        # Можно логировать, но не отвечать 
        logging.info(f"User pressed button: {user_text}") 
        return 
    await update.message.reply_text(f"You sent: {user_text}") 
 
def main(): 
    logging.basicConfig(level=logging.INFO) 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(MessageHandler(filters.TEXT, handle_message)) 
    logging.info("Bot starting...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
