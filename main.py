import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # САМАЯ ПРОСТАЯ КЛАВИАТУРА
    keyboard = [["TEST"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # САМОЕ ПРОСТОЕ СООБЩЕНИЕ
    await update.message.reply_text("Test keyboard:", reply_markup=markup)

def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()