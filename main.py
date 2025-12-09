# -*- coding: utf-8 -*- 
import os 
import logging 
from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
from dotenv import load_dotenv 
 
load_dotenv() 
 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [["Product", "Calculator"], ["Help"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("ARTBAZAR Bot", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text = update.message.text 
    if text == "Product": 
        await update.message.reply_text("Analyze product") 
    elif text == "Calculator": 
        await update.message.reply_text("Calculate margin") 
    elif text == "Help": 
        await update.message.reply_text("Help info") 
 
def main(): 
    if not BOT_TOKEN: 
        logger.error("No BOT_TOKEN") 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(MessageHandler(filters.TEXT, handle_message)) 
 
    logger.info("Starting bot...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
