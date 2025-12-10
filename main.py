import os 
import json 
import logging 
from datetime import datetime 
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler 
 
# ==================== КОНФИГУРАЦИЯ ==================== 
OWNER_ID = 1974482384 
MANAGER_IDS = [1974482384] 
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
 
# ==================== БАЗА ДАННЫХ ==================== 
def load_db(): 
    try: 
        with open("artbazar_db.json", "r", encoding="utf-8") as f: 
            return json.load(f) 
    except: 
        return {"users": {}, "analytics": 0, "revenue": 0, "premium_users": []} 
 
def save_db(db): 
    with open("artbazar_db.json", "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=2, ensure_ascii=False) 
 
def get_user(user_id): 
    db = load_db() 
    uid = str(user_id) 
    if uid not in db["users"]: 
        db["users"][uid] = { 
            "daily_used": 0, 
            "last_reset": datetime.now().strftime("%Y-%m-%d"), 
            "lang": "RU", 
            "total_analytics": 0, 
            "premium_until": None, 
            "join_date": datetime.now().strftime("%Y-%m-%d"), 
            "username": "" 
        } 
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
 
# ==================== ОСНОВНЫЕ ФУНКЦИИ ==================== 
async def show_user_menu(update, user_id): 
    user = get_user(user_id) 
    menu_text = f"🎯 *ARTBAZAR AI*\\nАнализов сегодня: {user['daily_used']}/{FREE_DAILY_LIMIT}\\n\\nВыберите опцию:" 
    keyboard = [ 
        ["🚀 СКРИНИНГ ТОВАРА", "📈 ПРОФИЛЬ НИШИ"], 
        ["💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ", "💎 ARTBAZAR PRO"], 
        ["🌐 ЯЗЫК", "❓ ПОМОЩЬ"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def show_manager_menu(update, user_id): 
    db = load_db() 
    menu_text = f"👨‍💼 *МЕНЕДЖЕР ПАНЕЛЬ*\\nПользователи: {len(db['users'])}" 
    keyboard = [ 
        ["📊 СТАТИСТИКА", "👥 ПОЛЬЗОВАТЕЛИ"], 
        ["⬅️ НАЗАД"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def show_owner_menu(update, user_id): 
    db = load_db() 
    menu_text = f"👑 *БИЗНЕС ПАНЕЛЬ*\\nПользователи: {len(db['users'])}" 
    keyboard = [ 
        ["📊 ФИНАНСЫ", "👥 ЮЗЕРЫ"], 
        ["⚙️ НАСТРОЙКИ", "🔄 СБРОС"], 
        ["⬅️ К ПОЛЬЗОВАТЕЛЮ"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
 
    if user_id == OWNER_ID: 
        await show_owner_menu(update, user_id) 
    elif user_id in MANAGER_IDS: 
        await show_manager_menu(update, user_id) 
    else: 
        keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
        await update.message.reply_text("🌐 *ARTBAZAR AI*\\nВыберите язык:", parse_mode="Markdown", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    text = update.message.text 
 
    # Выбор языка 
    if text in ["🇷🇺 Русский", "🇰🇿 Қазақша", "🇰🇬 Кыргызча"]: 
        await show_user_menu(update, user_id) 
        return 
 
    # Интерфейс пользователя 
    if user_id not in MANAGER_IDS: 
        if text == "🚀 СКРИНИНГ ТОВАРА": 
            await update.message.reply_text("🎯 *Введите название товара:*", parse_mode="Markdown") 
            context.user_data["mode"] = "product_analysis" 
        elif text == "📈 ПРОФИЛЬ НИШИ": 
            niches = "\\n".join([f"• {n}" for n in MARKET_DATA.keys()]) 
            await update.message.reply_text(f"📊 *Выберите нишу:*\\n{niches}", parse_mode="Markdown") 
            context.user_data["mode"] = "niche_analysis" 
        elif text == "💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ": 
            await update.message.reply_text("🧮 *Введите данные:*\\nПример: 5000 | 8000", parse_mode="Markdown") 
            context.user_data["mode"] = "margin_analysis" 
        elif text == "💎 ARTBAZAR PRO": 
            await update.message.reply_text(f"💎 *ARTBAZAR PRO*\\nОплата: {MANAGER_USERNAME}", parse_mode="Markdown") 
        elif text == "🌐 ЯЗЫК": 
            keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча", "⬅️ Назад"]] 
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
            await update.message.reply_text("🌐 Выберите язык:", reply_markup=markup) 
        elif text == "❓ ПОМОЩЬ": 
            await update.message.reply_text("❓ *Помощь*\\nОбратитесь к @artbazar_support", parse_mode="Markdown") 
        elif text == "⬅️ Назад": 
            await show_user_menu(update, user_id) 
 
        # Обработка анализов 
        elif context.user_data.get("mode") == "product_analysis": 
            if check_limit(user_id): 
                use_analysis(user_id) 
                import random 
                niche = random.choice(list(MARKET_DATA.keys())) 
                data = MARKET_DATA[niche] 
                analysis = f"🎯 *Анализ товара*\\nТовар: {text}\\nНиша: {niche}\\nСпрос: {random.randint(50000,500000):,}/мес\\nМаржа: {random.randint(25,70)}%\\nРекомендация: ✅ Перспективный" 
                await update.message.reply_text(analysis, parse_mode="Markdown") 
            else: 
                await update.message.reply_text(f"❌ *Лимит исчерпан*\\nОбратитесь к {MANAGER_USERNAME}", parse_mode="Markdown") 
            context.user_data["mode"] = None 
 
        elif context.user_data.get("mode") == "niche_analysis": 
            if text in MARKET_DATA: 
                if check_limit(user_id): 
                    use_analysis(user_id) 
                    data = MARKET_DATA[text] 
                    analysis = f"📈 *Анализ ниши*\\nНиша: {text}\\nСпрос: {data['спрос']:,}/мес\\nКонкуренция: {data['конкуренция']}\\nМаржа: {data['маржа']}%" 
                    await update.message.reply_text(analysis, parse_mode="Markdown") 
                else: 
                    await update.message.reply_text(f"❌ *Лимит исчерпан*", parse_mode="Markdown") 
            else: 
                await update.message.reply_text("❌ Ниша не найдена", parse_mode="Markdown") 
            context.user_data["mode"] = None 
 
        elif context.user_data.get("mode") == "margin_analysis": 
            try: 
                cost, price = [float(x.strip()) for x in text.split("|")] 
                profit = price - cost 
                margin = (profit / price) * 100 
                result = f"🧮 *Маржинальный анализ*\\nПрибыль: {profit:,.0f} ₸\\nМаржа: {margin:.1f}%" 
                await update.message.reply_text(result, parse_mode="Markdown") 
            except: 
                await update.message.reply_text("❌ Ошибка формата", parse_mode="Markdown") 
            context.user_data["mode"] = None 
 
    # Интерфейс менеджера/владельца 
    else: 
        if text == "📊 СТАТИСТИКА": 
            db = load_db() 
            stats = f"📊 *Статистика*\\nПользователи: {len(db['users'])}" 
            await update.message.reply_text(stats, parse_mode="Markdown") 
        elif text == "👥 ПОЛЬЗОВАТЕЛИ": 
            db = load_db() 
            users = f"👥 *Пользователи*\\nВсего: {len(db['users'])}" 
            await update.message.reply_text(users, parse_mode="Markdown") 
        elif text == "⬅️ НАЗАД": 
            if user_id == OWNER_ID: 
                await show_owner_menu(update, user_id) 
            else: 
                await show_manager_menu(update, user_id) 
        elif text == "📊 ФИНАНСЫ": 
            await update.message.reply_text("💰 *Финансы*\\nВыручка: 0 сом", parse_mode="Markdown") 
        elif text == "👥 ЮЗЕРЫ": 
            db = load_db() 
            await update.message.reply_text(f"👥 *Юзеры*\\nВсего: {len(db['users'])}", parse_mode="Markdown") 
        elif text == "⚙️ НАСТРОЙКИ": 
            await update.message.reply_text("⚙️ *Настройки*\\nЛимит: 3 анализа/день", parse_mode="Markdown") 
        elif text == "🔄 СБРОС": 
            db = load_db() 
            for user in db["users"].values(): 
                user["daily_used"] = 0 
            save_db(db) 
            await update.message.reply_text("✅ Лимиты сброшены", parse_mode="Markdown") 
        elif text == "⬅️ К ПОЛЬЗОВАТЕЛЮ": 
            await show_user_menu(update, user_id) 
 
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
