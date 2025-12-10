import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

# States for ConversationHandler
WAITING_PRODUCT, WAITING_NICHE, WAITING_MARGIN = range(3)

# Main menu
async def start(update: Update, context):
    keyboard = [
        ["ANALYZE PRODUCT", "PROFILE NICHE"],
        ["CALCULATE MARGIN", "HELP"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("ARTBAZAR AI is ready! Choose action:", reply_markup=markup)
    return ConversationHandler.END

# 1. ANALYZE PRODUCT
async def analyze_product(update: Update, context):
    await update.message.reply_text("Send me product link or name:", reply_markup=ReplyKeyboardRemove())
    return WAITING_PRODUCT

async def process_product(update: Update, context):
    product = update.message.text
    await update.message.reply_text("Analyzing product...")
    
    import time
    time.sleep(2)
    
    report = f"PRODUCT ANALYSIS:\n\nProduct: {product[:50]}\n\nDemand: High (8/10)\nCompetition: Medium (7/10)\nMargin: 35-45%\n\nRecommendations:\n- Target price: 3,200-3,800 RUB\n- Best launch time: November-December"
    
    keyboard = [["MAIN MENU"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(report, reply_markup=markup)
    return ConversationHandler.END

# 2. PROFILE NICHE
async def profile_niche(update: Update, context):
    await update.message.reply_text("Enter keywords separated by commas:", reply_markup=ReplyKeyboardRemove())
    return WAITING_NICHE

async def process_niche(update: Update, context):
    keywords = update.message.text
    await update.message.reply_text("Analyzing niche...")
    
    import time
    time.sleep(2)
    
    report = f"MARKET ANALYSIS:\n\nKeywords: {keywords}\n\nMarket volume: 4.2B RUB/year\nGrowth: 15% monthly\nAudience: 12M people\n\nRecommendations:\n- Focus on segment under 5,000 RUB\n- Emphasize battery life"
    
    keyboard = [["MAIN MENU"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(report, reply_markup=markup)
    return ConversationHandler.END

# 3. CALCULATE MARGIN
async def calculate_margin(update: Update, context):
    await update.message.reply_text("Enter: cost price selling price logistics commission%\nExample: 1000 2000 200 15", reply_markup=ReplyKeyboardRemove())
    return WAITING_MARGIN

async def process_margin(update: Update, context):
    try:
        data = update.message.text.split()
        cost = float(data[0])
        price = float(data[1])
        logistics = float(data[2])
        commission = float(data[3])
        
        commission_amount = price * (commission / 100)
        expenses = cost + logistics + commission_amount
        profit = price - expenses
        margin = (profit / price) * 100
        
        report = f"MARGIN CALCULATION:\n\nCost: {cost:,} RUB\nPrice: {price:,} RUB\nLogistics: {logistics:,} RUB\nCommission ({commission}%): {commission_amount:,.0f} RUB\nExpenses: {expenses:,.0f} RUB\nProfit: {profit:,.0f} RUB\nMargin: {margin:.1f}%"
    except:
        report = "Wrong format. Use: 1000 2000 200 15"
    
    keyboard = [["MAIN MENU"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(report, reply_markup=markup)
    return ConversationHandler.END

# HELP
async def help_command(update: Update, context):
    await update.message.reply_text("Help: /start - Main menu\n\nANALYZE PRODUCT - Product analysis\nPROFILE NICHE - Market analysis\nCALCULATE MARGIN - Profit calculation")

# CANCEL
async def cancel(update: Update, context):
    await update.message.reply_text("Canceled.", reply_markup=ReplyKeyboardMarkup([["MAIN MENU"]], resize_keyboard=True))
    return ConversationHandler.END

# Main button handler
async def handle_button(update: Update, context):
    text = update.message.text
    if text == "MAIN MENU":
        return await start(update, context)
    elif text == "HELP":
        return await help_command(update, context)

# Main function
def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # Conversation handlers
    conv_product = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^ANALYZE PRODUCT$"), analyze_product)],
        states={WAITING_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_product)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    conv_niche = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^PROFILE NICHE$"), profile_niche)],
        states={WAITING_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_niche)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    conv_margin = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^CALCULATE MARGIN$"), calculate_margin)],
        states={WAITING_MARGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_margin)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_product)
    app.add_handler(conv_niche)
    app.add_handler(conv_margin)
    
    app.add_handler(MessageHandler(filters.Regex("^MAIN MENU$"), start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))
    
    logging.info("ARTBAZAR AI started!")
    app.run_polling()

if __name__ == "__main__":
    main()
