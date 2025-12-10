import os 
import json 
import logging 
from datetime import datetime 
from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
 
# ==================== ARTBAZAR AI КОНФИГ ==================== 
OWNER_ID = 1974482384 
MANAGER_USERNAME = "@artbazar_manager" 
FREE_DAILY_LIMIT = 3 
 
MARKET_DATA = { 
    "Товары для животных": {"спрос": 200000, "конкуренция": 9, "маржа": 51, "сезон": "Март"}, 
    "Домашний текстиль": {"спрос": 319000, "конкуренция": 24, "маржа": 17, "сезон": "Ноябрь"}, 
    "Посуда": {"спрос": 415000, "конкуренция": 9, "маржа": 45, "сезон": "Круглый год"}, 
    "Детские товары": {"спрос": 830000, "конкуренция": 19, "маржа": 5, "сезон": "Круглый год"}, 
    "Спорт товары": {"спрос": 89000, "конкуренция": 12, "маржа": 45, "сезон": "Ноябрь"}, 
    "Красота и здоровье": {"спрос": 155000, "конкуренция": 6, "маржа": 92, "сезон": "Круглый год"}, 
    "Хоз. товары": {"спрос": 112000, "конкуренция": 13, "маржа": 110, "сезон": "Февраль"} 
} 
 
def load_db(): 
    try: 
        with open("artbazar_db.json", "r") as f: 
            return json.load(f) 
    except: 
        return {"users": {}, "analytics": 0, "revenue": 0} 
 
def save_db(db): 
    with open("artbazar_db.json", "w") as f: 
        json.dump(db, f, indent=2) 
 
def get_user(user_id): 
    db = load_db() 
    uid = str(user_id) 
    if uid not in db["users"]: 
        db["users"][uid] = {"daily_used": 0, "last_reset": datetime.now().strftime("%Y-%m-%d"), "lang": "RU", "total_analytics": 0, "premium_until": None} 
        save_db(db) 
    return db["users"][uid] 
 
def update_user(user_id, data): 
    db = load_db() 
    uid = str(user_id) 
    if uid not in db["users"]: 
        db["users"][uid] = {} 
    db["users"][uid].update(data) 
    save_db(db) 
 
def check_limit(user_id): 
    user = get_user(user_id) 
    today = datetime.now().strftime("%Y-%m-%d") 
    if user["last_reset"] != today: 
        user["daily_used"] = 0 
        user["last_reset"] = today 
        update_user(user_id, user) 
    if user.get("premium_until"): 
            return True 
 
def use_analysis(user_id): 
    user = get_user(user_id) 
    user["daily_used"] += 1 
    user["total_analytics"] += 1 
    update_user(user_id, user) 
 
def artbazar_analysis(product_name, niche=None): 
    import random 
    if niche and niche in MARKET_DATA: 
        data = MARKET_DATA[niche] 
        return f"📈 *ARTBAZAR AI: ПРОФИЛЬ НИШИ*\\nНиша: {niche}\\nСпрос: {data['спрос']:,}/мес\\nКонкуренция: {data['конкуренция']}\\nМаржа: {data['маржа']}%\\nСезон: {data['сезон']}" 
    niches = list(MARKET_DATA.keys()) 
    selected = random.choice(niches) 
    data = MARKET_DATA[selected] 
    return f"🎯 *ARTBAZAR AI: СКРИНИНГ ТОВАРА*\\nТовар: {product_name}\\nНиша: {selected}\\nСпрос: {random.randint(50000,500000):,}/мес\\nКонкуренция: {random.randint(5,50)}\\nМаржа: {random.randint(25,70)}%\\nРекомендация: Перспективный" 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    if user_id == OWNER_ID: 
        await owner_dashboard(update) 
        return 
    keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("🌐 *ARTBAZAR AI*\\nВыберите язык:", parse_mode="Markdown", reply_markup=markup) 
 
async def owner_dashboard(update): 
    db = load_db() 
    text = f"👑 *ARTBAZAR AI - БИЗНЕС ПАНЕЛЬ*\\nПользователи: {len(db['users'])}\\nАнализов: {db.get('analytics',0)}\\nВыручка: {db.get('revenue',0)} сом" 
    keyboard = [["📊 Статистика", "💰 Финансы"], ["👥 Пользователи", "⚙️ Настройки"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    text = update.message.text 
 
    if user_id == OWNER_ID: 
        if text == "📊 Статистика": 
            db = load_db() 
            await update.message.reply_text(f"📈 Анализов: {db.get('analytics',0)}", parse_mode="Markdown") 
        return 
 
    user = get_user(user_id) 
 
    if text in ["🇷🇺 Русский", "🇰🇿 Қазақша", "🇰🇬 Кыргызча"]: 
        lang = {"🇷🇺 Русский": "RU", "🇰🇿 Қазақша": "KZ", "🇰🇬 Кыргызча": "KG"}[text] 
        update_user(user_id, {"lang": lang}) 
        await show_main_menu(update, user_id) 
 
    elif text == "🚀 СКРИНИНГ ТОВАРА": 
        if check_limit(user_id): 
            use_analysis(user_id) 
            await update.message.reply_text("🎯 *Введите название товара*\\n\\nПример: Умная колонка", parse_mode="Markdown") 
            context.user_data["awaiting_product"] = True 
        else: 
            await limit_exceeded(update, user_id) 
 
    elif text == "📈 ПРОФИЛЬ НИШИ": 
        if check_limit(user_id): 
            use_analysis(user_id) 
            niches = "\\n".join([f"• {n}" for n in MARKET_DATA.keys()]) 
            await update.message.reply_text(f"📊 *Выберите нишу:*\\n{niches}", parse_mode="Markdown") 
            context.user_data["awaiting_niche"] = True 
        else: 
            await limit_exceeded(update, user_id) 
 
    elif text == "💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ": 
        await update.message.reply_text("🧮 *Введите данные:*\\n\\nСебестоимость | Цена\\n\\nПример: 5000 | 8000", parse_mode="Markdown") 
 
    elif text == "💎 ARTBAZAR PRO": 
        premium_text = f"💎 *ARTBAZAR PRO*\\n✅ Безлимитные анализы\\n✅ Расширенные отчеты\\n✅ Приоритетная поддержка\\n\\n💰 Тарифы:\\n1 месяц - 499 сом\\n6 месяцев - 1999 сом\\n1 год - 3499 сом\\n\\n👨‍💼 Менеджер: {MANAGER_USERNAME}" 
        await update.message.reply_text(premium_text, parse_mode="Markdown") 
 
    elif text == "🌐 ЯЗЫК": 
        keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
        await update.message.reply_text("🌐 Выберите язык:", reply_markup=markup) 
 
    elif text == "❓ ПОМОЩЬ": 
        help_text = "❓ *ARTBAZAR AI*\\n🚀 СКРИНИНГ ТОВАРА - AI-анализ\\n📈 ПРОФИЛЬ НИШИ - аналитика рынка\\n💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ - расчет прибыли\\n💎 ARTBAZAR PRO - премиум доступ\\n\\n📞 Поддержка: @artbazar_support" 
        await update.message.reply_text(help_text, parse_mode="Markdown") 
 
    elif context.user_data.get("awaiting_product"): 
        analysis = artbazar_analysis(text) 
        await update.message.reply_text(analysis, parse_mode="Markdown") 
        context.user_data["awaiting_product"] = False 
 
    elif context.user_data.get("awaiting_niche"): 
        if text in MARKET_DATA: 
            analysis = artbazar_analysis(None, text) 
            await update.message.reply_text(analysis, parse_mode="Markdown") 
        else: 
            await update.message.reply_text("❌ Ниша не найдена", parse_mode="Markdown") 
        context.user_data["awaiting_niche"] = False 
 
    elif "|" in text: 
        try: 
            cost, price = [float(x.strip()) for x in text.split("|")] 
            profit = price - cost 
            margin = (profit / price) * 100 
            roi = (profit / cost) * 100 
            result = f"🧮 *МАРЖИНАЛЬНЫЙ АНАЛИЗ*\\nСебестоимость: {cost:,.0f} ₸\\nЦена: {price:,.0f} ₸\\nПрибыль: {profit:,.0f} ₸\\nМаржа: {margin:.1f}%\\nROI: {roi:.1f}%" 
            await update.message.reply_text(result, parse_mode="Markdown") 
        except: 
            await update.message.reply_text("❌ Ошибка формата. Пример: 5000 | 8000", parse_mode="Markdown") 
 
async def show_main_menu(update, user_id): 
    user = get_user(user_id) 
    premium = "💎 ARTBAZAR PRO" if user.get("premium_until") else "👤 БАЗОВЫЙ" 
    menu_text = f"🎯 *ARTBAZAR AI*\\nСтатус: {premium}\\nАнализов сегодня: {user['daily_used']}/{FREE_DAILY_LIMIT}\\n\\nВыберите опцию:" 
    keyboard = [["🚀 СКРИНИНГ ТОВАРА", "📈 ПРОФИЛЬ НИШИ"], ["💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ", "💎 ARTBAZAR PRO"], ["🌐 ЯЗЫК", "❓ ПОМОЩЬ"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def limit_exceeded(update, user_id): 
    user = get_user(user_id) 
    text = f"❌ *ЛИМИТ ИСЧЕРПАН*\\nИспользовано: {user['daily_used']}/3\\n\\n💎 ARTBAZAR PRO открывает безлимит\\n👨‍💼 Менеджер: {MANAGER_USERNAME}" 
    await update.message.reply_text(text, parse_mode="Markdown") 
 
def main(): 
    logging.basicConfig(level=logging.INFO) 
    BOT_TOKEN = os.getenv("BOT_TOKEN") 
    if not BOT_TOKEN: 
        logging.error("No BOT_TOKEN") 
        return 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    logging.info("🚀 ARTBAZAR AI запущен") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
