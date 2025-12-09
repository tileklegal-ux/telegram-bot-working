import os 
import logging 
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler 
from dotenv import load_dotenv 
 
load_dotenv() 
 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 
 
# Constants for ConversationHandler 
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3) 
 
BOT_TOKEN = os.getenv("BOT_TOKEN") 
OWNER_ID = os.getenv("OWNER_ID", "1974482384") 
MANAGER_ID = os.getenv("MANAGER_ID", "571499876") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user = update.effective_user 
    reply_keyboard = [ 
        ["Product Analysis", "Margin Calculator"], 
        ["Niche Analysis", "Recommendations"], 
        ["Languages", "Help"] 
    ] 
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True) 
 
    welcome_text = f"" 
?? *ARTBAZAR - AI Product Analyst* 
 
?? *Bot capabilities:* 
 Product analysis: demand, competition, margin 
 Profit and ROI calculator 
 Pricing recommendations 
 Multilingual (Russian, English) 
 Different roles: buyer, seller, analyst 
 
? *Check product in 10 seconds!* 
    "" 
 
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=markup) 
 
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
?? *Help commands:* 
 
/start - Main menu 
/analyze - Product analysis 
/calc - Margin calculator 
/niche - Niche analysis 
/lang - Change language 
 
?? *Main functions:* 
 Demand and competition analysis 
 Profit and ROI calculation 
 Pricing recommendations 
 Multilingual interface 
    await update.message.reply_text(help_text, parse_mode="Markdown") 
 
def main(): 
    if not BOT_TOKEN: 
        logger.error("No BOT_TOKEN") 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CommandHandler("help", help_command)) 
 
    # Button handlers 
    app.add_handler(MessageHandler(filters.Regex("^(Product Analysis)$"), 
        lambda u, c: u.message.reply_text("?? Product Analysis: Send product name for analysis"))) 
    app.add_handler(MessageHandler(filters.Regex("^(Margin Calculator)$"), 
        lambda u, c: u.message.reply_text("?? Calculator: Enter: Cost | Selling Price\\nExample: 5000 | 8000"))) 
    app.add_handler(MessageHandler(filters.Regex("^(Niche Analysis)$"), 
        lambda u, c: u.message.reply_text("?? Niche Analysis: Enter niche name"))) 
    app.add_handler(MessageHandler(filters.Regex("^(Recommendations)$"), 
        lambda u, c: u.message.reply_text("?? Recommendations: 1. Optimize price\\n2. Improve SEO\\n3. Expand assortment"))) 
    app.add_handler(MessageHandler(filters.Regex("^(Languages)$"), 
        lambda u, c: u.message.reply_text("?? Languages: Russian / English\\nSelect language:"))) 
    app.add_handler(MessageHandler(filters.Regex("^(Help)$"), help_command)) 
 
    logger.info("Starting ARTBAZAR bot...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
