import os 
import json 
import logging 
from datetime import datetime, timedelta 
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton 
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes 
 
# ==================== КОНСТАНТЫ ==================== 
OWNER_ID = 1974482384  # 👑 Владелец 
MANAGER_USERNAME = "@artbazar_manager"  # 👨‍💼 Менеджер 
 
FREE_DAILY_LIMIT = 3  # 3 анализа/день бесплатно 
 
PREMIUM_TARIFFS = { 
    "1_month": {"price": 499, "days": 30}, 
    "6_months": {"price": 1999, "days": 180}, 
    "1_year": {"price": 3499, "days": 365} 
} 
 
# ==================== БАЗА ДАННЫХ ==================== 
def load_users(): 
    try: 
        with open("users_db.json", "r") as f: 
            return json.load(f) 
    except: 
        return {} 
 
def save_users(users): 
    with open("users_db.json", "w") as f: 
        json.dump(users, f, indent=2) 
 
def load_subscriptions(): 
    try: 
        with open("subscriptions_db.json", "r") as f: 
            return json.load(f) 
    except: 
        return {} 
 
def save_subscriptions(subs): 
    with open("subscriptions_db.json", "w") as f: 
        json.dump(subs, f, indent=2) 
 
# ==================== УТИЛИТЫ ==================== 
def get_user_data(user_id): 
    users = load_users() 
    if str(user_id) not in users: 
        users[str(user_id)] = { 
            "daily_used": 0, 
            "last_reset": datetime.now().strftime("%Y-%m-%d"), 
            "role": "user", 
            "lang": "RU", 
            "total_analyses": 0, 
            "premium_until": None 
        } 
        save_users(users) 
    return users[str(user_id)] 
 
def update_user_data(user_id, data): 
    users = load_users() 
    users[str(user_id)].update(data) 
    save_users(users) 
 
def check_daily_limit(user_id): 
    user = get_user_data(user_id) 
    today = datetime.now().strftime("%Y-%m-%d") 
 
    # Автосброс в 00:00 
    if user["last_reset"] != today: 
        user["daily_used"] = 0 
        user["last_reset"] = today 
        update_user_data(user_id, user) 
 
    # Проверка лимита 
    if user["premium_until"]: 
        premium_until = datetime.strptime(user["premium_until"], "%Y-%m-%d") 
            return True  # Премиум - безлимит 
 
 
def use_analysis(user_id): 
    user = get_user_data(user_id) 
    user["daily_used"] += 1 
    user["total_analyses"] += 1 
    update_user_data(user_id, user) 
 
# ==================== ОСНОВНЫЕ ФУНКЦИИ ==================== 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
 
    # 👑 Владелец 
    if user_id == OWNER_ID: 
        await owner_dashboard(update, context) 
        return 
 
    # Определяем язык 
    keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("🌐 *Выберите язык:*", parse_mode="Markdown", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    text = update.message.text 
 
    # 👑 Владелец обработка 
    if user_id == OWNER_ID: 
        if text == "📊 Статистика": 
            await show_statistics(update, context) 
        elif text == "💰 Финансы": 
            await show_finances(update, context) 
        elif text == "👥 Менеджеры": 
            await manage_managers(update, context) 
        return 
 
    # Обычные пользователи 
    if text in ["🇷🇺 Русский", "🇰🇿 Қазақша", "🇰🇬 Кыргызча"]: 
        lang = {"🇷🇺 Русский": "RU", "🇰🇿 Қазақша": "KZ", "🇰🇬 Кыргызча": "KG"}[text] 
        update_user_data(user_id, {"lang": lang}) 
        await show_main_menu(update, context, lang) 
 
    elif text == "📊 Анализ товара": 
        if check_daily_limit(user_id): 
            use_analysis(user_id) 
            await analyze_product(update, context) 
        else: 
            await update.message.reply_text("❌ *Лимит исчерпан!*\\n\\nВы использовали 3 бесплатных анализа сегодня.\\n\\n💎 *Премиум:* безлимитный доступ", parse_mode="Markdown") 
 
    elif text == "🧮 Калькулятор": 
        await calculate_margin(update, context) 
 
    elif text == "🔍 Анализ ниши": 
        if check_daily_limit(user_id): 
            use_analysis(user_id) 
            await analyze_niche(update, context) 
        else: 
            await update.message.reply_text("❌ Лимит исчерпан! Премиум: безлимит", parse_mode="Markdown") 
 
    elif text == "💡 Рекомендации": 
        await show_recommendations(update, context) 
 
    elif text == "💎 Премиум": 
        await show_premium(update, context) 
 
    elif text == "🌐 Язык": 
        await change_language(update, context) 
 
    elif text == "❓ Помощь": 
        await show_help(update, context) 
 
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str): 
    user_id = update.effective_user.id 
    user = get_user_data(user_id) 
 
    # Проверка премиума 
 
    welcome_text = f"🎯 *ARTBAZAR AI*\\n\\nСтатус: {premium_status}\\nАнализов сегодня: {user['daily_used']}/{FREE_DAILY_LIMIT}\\n\\nВыберите опцию:" 
 
    keyboard = [ 
        ["📊 Анализ товара", "🧮 Калькулятор"], 
        ["🔍 Анализ ниши", "💡 Рекомендации"], 
        ["💎 Премиум", "🌐 Язык", "❓ Помощь"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=markup) 
 
async def owner_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [["📊 Статистика"], ["💰 Финансы"], ["👥 Менеджеры"]] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("👑 *ПАНЕЛЬ ВЛАДЕЛЬЦА*\\n\\nВыберите раздел:", parse_mode="Markdown", reply_markup=markup) 
 
async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    users = load_users() 
    total_users = len(users) 
    total_analyses = sum(u.get("total_analyses", 0) for u in users.values()) 
    premium_users = sum(1 for u in users.values() if u.get("premium_until")) 
 
    stats = ( 
        "📊 *СТАТИСТИКА СИСТЕМЫ*\\n\\n" 
        f"👥 Всего пользователей: {total_users}\\n" 
        f"💎 Премиум пользователей: {premium_users}\\n" 
        f"📈 Всего анализов: {total_analyses}\\n" 
        f"🎯 Конверсия в премиум: {premium_users/total_users*100 if total_users > 0 else 0:.1f}%" 
    ) 
    await update.message.reply_text(stats, parse_mode="Markdown") 
 
async def show_finances(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    subs = load_subscriptions() 
    total_revenue = sum(s.get("price", 0) for s in subs.values()) 
 
    finances = ( 
        "💰 *ФИНАНСОВАЯ СТАТИСТИКА*\\n\\n" 
        f"💵 Общая выручка: {total_revenue} сом\\n" 
        f"💎 Активных подписок: {active_subs}\\n" 
        f"📅 ARPU: {total_revenue/active_subs if active_subs > 0 else 0:.0f} сом/пользователь" 
    ) 
    await update.message.reply_text(finances, parse_mode="Markdown") 
 
async def analyze_product(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    analysis = ( 
        "📊 *АНАЛИЗ ТОВАРА*\\n\\n" 
        "Отправьте название товара для анализа.\\n\\n" 
        "*Пример анализа:*\\n" 
        "• Корм Whiskas\\n" 
        "• Спрос: 200K/мес\\n" 
        "• Конкуренция: 9 продавцов\\n" 
        "• Маржа: 51%\\n" 
        "• Рентабельность: Высокая" 
    ) 
    await update.message.reply_text(analysis, parse_mode="Markdown") 
 
async def show_premium(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [ 
        ["1 месяц - 499 сом"], 
        ["6 месяцев - 1999 сом"], 
        ["1 год - 3499 сом"], 
        ["📞 Связаться с менеджером"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
 
    text = ( 
        "💎 *ПРЕМИУМ ПОДПИСКА*\\n\\n" 
        "✅ *Безлимитные анализы*\\n" 
        "✅ *Расширенные отчеты*\\n" 
        "✅ *Приоритетная поддержка*\\n\\n" 
        "*Тарифы:*\\n" 
        "1️⃣ 1 месяц - 499 сом\\n" 
        "2️⃣ 6 месяцев - 1999 сом\\n" 
        "3️⃣ 1 год - 3499 сом\\n\\n" 
        f"Для оформления: {MANAGER_USERNAME}" 
    ) 
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup) 
 
# Остальные функции (calculate_margin, analyze_niche, show_recommendations, show_help) 
# Добавим их позже чтобы код не был слишком длинным 
 
def main(): 
    BOT_TOKEN = os.getenv("BOT_TOKEN") 
    if not BOT_TOKEN: 
        logging.error("No BOT_TOKEN") 
        return 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
 
    logging.info("🚀 ARTBAZAR AI PRO запущен...") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
