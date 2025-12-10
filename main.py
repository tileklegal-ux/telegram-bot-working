import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["ANALYZE PRODUCT", "PROFILE NICHE"],
        ["CALCULATE MARGIN", "HELP"]
    ]
    markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True
    )
    await update.message.reply_text("ARTBAZAR AI ready! Choose:", reply_markup=markup)

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["ANALYZE PRODUCT", "PROFILE NICHE"],
        ["CALCULATE MARGIN", "HELP"]
    ]
    markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True
    )
    await update.message.reply_text("Keyboard shown!", reply_markup=markup)

async def hide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Keyboard hidden. Use /show to bring it back.", reply_markup=ReplyKeyboardRemove())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text in ["ANALYZE PRODUCT", "PROFILE NICHE", "CALCULATE MARGIN", "HELP"]:
        logging.info(f"User pressed button: {user_text}")
        # Здесь можно добавить обработку каждой кнопки
        if user_text == "HELP":
            await update.message.reply_text("This is help message. Other functions are in development.")
        else:
            await update.message.reply_text(f"Function '{user_text}' is in development.")
        return
    await update.message.reply_text(f"You sent: {user_text}")

def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler("hide", hide))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    logging.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()