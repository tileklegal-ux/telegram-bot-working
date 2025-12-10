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
    await update.message.reply_text(f"Pressed: {update.message.text}") 
 
def main(): 
    logging.basicConfig(level=logging.INFO) 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
