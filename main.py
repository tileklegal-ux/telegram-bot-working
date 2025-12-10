# -*- coding: utf-8 -*- 
import os 
import logging 
from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
 
    keyboard = [ 
        ["ANALIZ TOVARA", "PROFIL NISHI"], 
        ["RASCHET MARZHI", "POMOSH"] 
    ] 
 
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False) 
 
    await update.message.reply_text( 
        text="Test bot rabotayet! Viborite:", 
        reply_markup=reply_markup 
    ) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text(f"Vi nazhali: {update.message.text}") 
 
def main(): 
    logging.basicConfig(level=logging.INFO) 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(MessageHandler(filters.TEXT  filters.COMMAND, handle_message)) 
    logging.info("Bot zapushen!") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
