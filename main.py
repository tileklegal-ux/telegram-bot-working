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
    reply_keyboard = [ 
        ["Product Analysis", "Margin Calculator"], 
        ["Niche Analysis", "Recommendations"], 
        ["Languages", "Help"] 
    ] 
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True) 
 
*ARTBAZAR - AI Product Analyst* 
 
*Bot capabilities:* 
- Product analysis: demand, competition, margin 
- Profit and ROI calculator 
- Pricing recommendations 
- Multilingual interface 
- Different roles: buyer, seller, analyst 
 
*Check product in 10 seconds!* 
 
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text = update.message.text 
 
    if text == "Product Analysis": 
        await update.message.reply_text("Send product name for analysis") 
    elif text == "Margin Calculator": 
        await update.message.reply_text("Enter: Cost | Price\\nExample: 5000 | 8000") 
    elif text == "Niche Analysis": 
        await update.message.reply_text("Enter niche name for analysis") 
    elif text == "Recommendations": 
        await update.message.reply_text("1. Optimize price\\n2. Improve SEO\\n3. Expand assortment") 
    elif text == "Languages": 
        await update.message.reply_text("Select language: Russian / English") 
    elif text == "Help": 
        await update.message.reply_text("Commands: /start, /help\\nButtons for all functions") 
    else: 
        await update.message.reply_text(f"You selected: {text}") 
 
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("Help: Use buttons or commands") 
 
def main(): 
    if not BOT_TOKEN: 
        logger.error("No BOT_TOKEN") 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CommandHandler("help", help_command)) 
 
    logger.info("Starting ARTBAZAR bot...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
