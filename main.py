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
 
TEXTS = { 
    "welcome": "*ARTBAZAR - AI Аналитик Товаров*\\n\\nАнализ за 10 секунд:\\n✅ Спрос и конкуренция\\n✅ Маржа и рентабельность\\n✅ Рекомендации", 
    "product": "📊 Анализ товара", 
    "margin": "🧮 Калькулятор маржи", 
    "niche": "🔍 Анализ ниши", 
    "recommend": "💡 Рекомендации", 
    "lang": "🌐 Язык", 
    "help": "❓ Помощь", 
    "owner": "👑 Владелец", 
    "manager": "📋 Менеджер", 
    "user": "👤 Пользователь" 
} 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("🌐 Выберите язык", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text = update.message.text 
 
    if text == "🇷🇺 Русский": 
        await show_main_menu(update, context) 
    elif text == "🇰🇿 Қазақша": 
        await update.message.reply_text("🇰🇿 Рус тілінде жалғастырайық", reply_markup=ReplyKeyboardMarkup([["🇷🇺 Русский"]], resize_keyboard=True)) 
    elif text == "🇰🇬 Кыргызча": 
        await update.message.reply_text("🇰🇬 Орус тилинде улантайлы", reply_markup=ReplyKeyboardMarkup([["🇷🇺 Русский"]], resize_keyboard=True)) 
 
    elif text == TEXTS["product"]: 
        await update.message.reply_text("📦 Отправьте название товара") 
    elif text == TEXTS["margin"]: 
        await update.message.reply_text("🧮 Введите: стоимость | цена") 
    elif text == TEXTS["niche"]: 
        await update.message.reply_text("🔍 Введите нишу") 
    elif text == TEXTS["recommend"]: 
        await update.message.reply_text("💡 Рекомендации...") 
    elif text == TEXTS["lang"]: 
        await change_language(update, context) 
    elif text == TEXTS["help"]: 
        await update.message.reply_text("❓ Помощь...") 
    elif text in [TEXTS["owner"], TEXTS["manager"], TEXTS["user"]]: 
        await update.message.reply_text(f"✅ Роль: {text}") 
 
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [[TEXTS["owner"], TEXTS["manager"], TEXTS["user"]]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("👥 Выберите роль:", reply_markup=markup) 
 
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("🌐 Выберите язык:", reply_markup=markup) 
 
def get_main_keyboard(): 
    keyboard = [ 
        [TEXTS["product"], TEXTS["margin"]], 
        [TEXTS["niche"], TEXTS["recommend"]], 
        [TEXTS["lang"], TEXTS["help"]] 
    ] 
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
 
def main(): 
    if not BOT_TOKEN: 
        logger.error("No BOT_TOKEN") 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CommandHandler("help", show_help)) 
    logger.info("🚀 ARTBAZAR AI запущен...") 
    app.run_polling() 
 
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text("❓ Помощь: /start - начать", reply_markup=get_main_keyboard()) 
 
if __name__ == "__main__": 
    main() 
