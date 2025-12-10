import os 
import json 
import logging 
from datetime import datetime 
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler 
 
# ==================== ARTBAZAR AI КОНФИГ ==================== 
OWNER_ID = 1974482384 
MANAGER_IDS = [1974482384]  # Временно владелец тоже менеджер 
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
 
def increment_analytics(): 
    db = load_db() 
    db["analytics"] = db.get("analytics", 0) + 1 
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
    increment_analytics() 
 
# ==================== AI АНАЛИЗ ==================== 
def artbazar_analysis(product_name, niche=None): 
    import random 
    if niche and niche in MARKET_DATA: 
        data = MARKET_DATA[niche] 
        return f"📈 *ARTBAZAR AI: ПРОФИЛЬ НИШИ*\\n\\n🏷 Ниша: {niche}\\n📊 Спрос: {data['спрос']:,}/мес\\n⚡ Конкуренция: {data['конкуренция']}/100\\n💰 Маржа: {data['маржа']}%\\n📅 Сезон: {data['сезон']}\\n\\n🎯 Рекомендация: {'Рекомендуем' if data['маржа'] > 30 else 'Требует анализа'}" 
    niches = list(MARKET_DATA.keys()) 
    selected = random.choice(niches) 
    data = MARKET_DATA[selected] 
    return f"🎯 *ARTBAZAR AI: СКРИНИНГ ТОВАРА*\\n\\n🏷 Товар: {product_name}\\n📊 Ниша: {selected}\\n📈 Спрос: {random.randint(50000,500000):,}/мес\\n⚡ Конкуренция: {random.randint(5,50)}/100\\n💰 Маржа: {random.randint(25,70)}%\\n\\n🎯 Рекомендация: {'✅ Перспективный' if random.randint(1,10) > 3 else '⚠️ Требует анализа'}" 
 
# ==================== ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ ==================== 
async def show_user_menu(update, user_id): 
    user = get_user(user_id) 
    premium = "💎 ARTBAZAR PRO" if user.get("premium_until") else "👤 БАЗОВЫЙ" 
    menu_text = f"🎯 *ARTBAZAR AI - БИЗНЕС АНАЛИТИК*\\n\\n📊 Статус: {premium}\\n📈 Анализов сегодня: {user['daily_used']}/{FREE_DAILY_LIMIT}\\n\\nВыберите опцию:" 
    keyboard = [ 
        ["🚀 СКРИНИНГ ТОВАРА", "📈 ПРОФИЛЬ НИШИ"], 
        ["💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ", "💎 ARTBAZAR PRO"], 
        ["🌐 ЯЗЫК", "❓ ПОМОЩЬ"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def user_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text = update.message.text 
    user_id = update.effective_user.id 
 
    if text == "🚀 СКРИНИНГ ТОВАРА": 
        if check_limit(user_id): 
            await update.message.reply_text("🎯 *Введите название товара:*\\n\\nПример: Умная колонка Яндекс Станция", parse_mode="Markdown") 
            context.user_data["awaiting_product"] = True 
        else: 
            await limit_exceeded(update, user_id) 
 
    elif text == "📈 ПРОФИЛЬ НИШИ": 
        if check_limit(user_id): 
            niches = "\\n".join([f"• {n}" for n in MARKET_DATA.keys()]) 
            await update.message.reply_text(f"📊 *Выберите нишу:*\\n\\n{niches}", parse_mode="Markdown") 
            context.user_data["awaiting_niche"] = True 
        else: 
            await limit_exceeded(update, user_id) 
 
    elif text == "💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ": 
        await update.message.reply_text("🧮 *Введите данные:*\\n\\nСебестоимость | Цена\\n\\nПример: 5000 | 8000", parse_mode="Markdown") 
        context.user_data["awaiting_margin"] = True 
 
    elif text == "💎 ARTBAZAR PRO": 
        keyboard = [ 
            [InlineKeyboardButton("1 месяц - 499 сом", callback_data="premium_1")], 
            [InlineKeyboardButton("6 месяцев - 1999 сом", callback_data="premium_6")], 
            [InlineKeyboardButton("1 год - 3499 сом", callback_data="premium_12")] 
        ] 
        markup = InlineKeyboardMarkup(keyboard) 
        premium_text = f"💎 *ARTBAZAR PRO*\\n\\n✅ Безлимитные анализы\\n✅ Расширенные отчеты\\n✅ Приоритетная поддержка\\n✅ Экспорт в Excel\\n\\n👨‍💼 Консультация: {MANAGER_USERNAME}" 
        await update.message.reply_text(premium_text, parse_mode="Markdown", reply_markup=markup) 
 
    elif text == "🌐 ЯЗЫК": 
        keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча", "⬅️ Назад"]] 
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
        await update.message.reply_text("🌐 *Выберите язык:*", parse_mode="Markdown", reply_markup=markup) 
 
    elif text == "❓ ПОМОЩЬ": 
        help_text = "❓ *ARTBAZAR AI - ПОМОЩЬ*\\n\\n🚀 СКРИНИНГ ТОВАРА - AI-анализ товара\\n📈 ПРОФИЛЬ НИШИ - аналитика рынка\\n💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ - расчет прибыли\\n💎 ARTBAZAR PRO - премиум доступ\\n\\n📞 Поддержка: @artbazar_support" 
        await update.message.reply_text(help_text, parse_mode="Markdown") 
 
    elif text == "⬅️ Назад": 
        await show_user_menu(update, user_id) 
 
    elif text in ["🇷🇺 Русский", "🇰🇿 Қазақша", "🇰🇬 Кыргызча"]: 
        lang = {"🇷🇺 Русский": "RU", "🇰🇿 Қазақша": "KZ", "🇰🇬 Кыргызча": "KG"}[text] 
        update_user(user_id, {"lang": lang}) 
        await update.message.reply_text(f"✅ Язык изменен на {text}", parse_mode="Markdown") 
        await show_user_menu(update, user_id) 
 
    elif context.user_data.get("awaiting_product"): 
        if check_limit(user_id): 
            use_analysis(user_id) 
            analysis = artbazar_analysis(text) 
            await update.message.reply_text(analysis, parse_mode="Markdown") 
        else: 
            await limit_exceeded(update, user_id) 
        context.user_data["awaiting_product"] = False 
 
    elif context.user_data.get("awaiting_niche"): 
        if text in MARKET_DATA: 
            if check_limit(user_id): 
                use_analysis(user_id) 
                analysis = artbazar_analysis(None, text) 
                await update.message.reply_text(analysis, parse_mode="Markdown") 
            else: 
                await limit_exceeded(update, user_id) 
        else: 
            await update.message.reply_text("❌ *Ниша не найдена*\\nИспользуйте список выше", parse_mode="Markdown") 
        context.user_data["awaiting_niche"] = False 
 
    elif context.user_data.get("awaiting_margin"): 
        try: 
            cost, price = [float(x.strip()) for x in text.split("|")] 
            profit = price - cost 
            margin = (profit / price) * 100 
            roi = (profit / cost) * 100 
            result = f"🧮 *МАРЖИНАЛЬНЫЙ АНАЛИЗ*\\n\\n📦 Себестоимость: {cost:,.0f} ₸\\n💰 Цена: {price:,.0f} ₸\\n💵 Прибыль: {profit:,.0f} ₸\\n📊 Маржа: {margin:.1f}%\\n🚀 ROI: {roi:.1f}%\\n\\n{'✅ Рентабельно' if margin > 30 else '⚠️ Низкая маржа'}" 
            await update.message.reply_text(result, parse_mode="Markdown") 
        except: 
            await update.message.reply_text("❌ *Ошибка формата*\\nПример: 5000 | 8000", parse_mode="Markdown") 
        context.user_data["awaiting_margin"] = False 
 
# ==================== ИНТЕРФЕЙС МЕНЕДЖЕРА ==================== 
async def show_manager_menu(update, user_id): 
    db = load_db() 
    active_users = 0 
    for u in db["users"].values(): 
        if u.get("total_analytics", 0) 
            active_users += 1 
    menu_text = f"👨‍💼 *ARTBAZAR AI - МЕНЕДЖЕР ПАНЕЛЬ*\\n\\n👥 Пользователи: {len(db['users'])}\\n📊 Активные: {active_users}\\n💰 Выручка: {db.get('revenue', 0):,} сом" 
    keyboard = [ 
        ["📊 СТАТИСТИКА", "👥 ПОЛЬЗОВАТЕЛИ"], 
        ["💎 ПРЕМИУМ", "📈 АНАЛИТИКА"], 
        ["⬅️ В МЕНЮ"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def manager_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text = update.message.text 
    user_id = update.effective_user.id 
 
    if text == "⬅️ В МЕНЮ": 
        await show_manager_menu(update, user_id) 
 
    elif text == "📊 СТАТИСТИКА": 
        db = load_db() 
        stats = f"📊 *СТАТИСТИКА СИСТЕМЫ*\\n\\n👥 Всего пользователей: {len(db['users']):,}\\n📈 Всего анализов: {db.get('analytics', 0):,}\\n💰 Выручка: {db.get('revenue', 0):,} сом\\n💎 Премиум пользователей: {len(db.get('premium_users', []))}" 
        await update.message.reply_text(stats, parse_mode="Markdown") 
 
    elif text == "👥 ПОЛЬЗОВАТЕЛИ": 
        db = load_db() 
        user_items = list(db["users"].items()) 
        recent_users = user_items[-10:] if len(user_items)  else user_items 
        users_text = "👥 *ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ*\\n\\n" 
        for uid, user in recent_users: 
            users_text += f"ID: {uid[:8]}... | Анализов: {user.get('total_analytics', 0)}\\n" 
        users_text += "\\n📊 Используйте /user ID для деталей" 
        await update.message.reply_text(users_text, parse_mode="Markdown") 
 
    elif text == "💎 ПРЕМИУМ": 
        premium_text = "💎 *УПРАВЛЕНИЕ ПРЕМИУМ*\\n\\n1. Добавить премиум: /premium_add ID срок\\n2. Удалить премиум: /premium_remove ID\\n3. Список премиум: /premium_list" 
        await update.message.reply_text(premium_text, parse_mode="Markdown") 
 
    elif text == "📈 АНАЛИТИКА": 
        db = load_db() 
        user_list = [] 
        for uid, u in db["users"].items(): 
            user_list.append((uid, u.get("total_analytics", 0))) 
        user_list.sort(key=lambda x: x[1], reverse=True) 
        top_users = user_list[:5] 
        analytics = "📈 *ТОП-5 АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ*\\n\\n" 
        for i, (uid, count) in enumerate(top_users, 1): 
            analytics += f"{i}. ID: {uid[:8]}... - {count} анализов\\n" 
        await update.message.reply_text(analytics, parse_mode="Markdown") 
 
# ==================== ИНТЕРФЕЙС ВЛАДЕЛЬЦА ==================== 
async def show_owner_menu(update, user_id): 
    db = load_db() 
    menu_text = f"👑 *ARTBAZAR AI - БИЗНЕС ПАНЕЛЬ*\\n\\n👥 Пользователи: {len(db['users']):,}\\n📊 Анализов: {db.get('analytics', 0):,}\\n💰 Выручка: {db.get('revenue', 0):,} сом\\n💎 Премиум: {len(db.get('premium_users', []))}" 
    keyboard = [ 
        ["📊 ФИНАНСЫ", "👥 ЮЗЕРЫ"], 
        ["⚙️ НАСТРОЙКИ", "📈 ГРАФИКИ"], 
        ["🔄 СБРОС ЛИМИТОВ", "📤 ЭКСПОРТ"], 
        ["⬅️ К ПОЛЬЗОВАТЕЛЮ"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def owner_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    text = update.message.text 
    user_id = update.effective_user.id 
 
    if text == "⬅️ К ПОЛЬЗОВАТЕЛЮ": 
        await show_user_menu(update, user_id) 
 
    elif text == "📊 ФИНАНСЫ": 
        db = load_db() 
        premium_count = len(db.get("premium_users", [])) 
        avg_check = db.get("revenue", 0) / max(1, premium_count) 
        finance = f"💰 *ФИНАНСОВАЯ АНАЛИТИКА*\\n\\n💵 Общая выручка: {db.get('revenue', 0):,} сом\\n📊 Средний чек: {avg_check:,.0f} сом\\n💎 Премиум подписок: {premium_count}\\n🔄 Ежемесячный рост: +15%" 
        await update.message.reply_text(finance, parse_mode="Markdown") 
 
    elif text == "👥 ЮЗЕРЫ": 
        db = load_db() 
        today = datetime.now().strftime("%Y-%m-%d") 
        new_today = 0 
        for u in db["users"].values(): 
            if u.get("join_date") == today: 
                new_today += 1 
        total_users = len(db["users"]) 
        revenue = db.get("revenue", 0) 
        premium_count = len(db.get("premium_users", [])) 
        arpu = revenue / max(1, total_users) 
        conversion = (premium_count / max(1, total_users)) * 100 
        users = f"👥 *АНАЛИТИКА ПОЛЬЗОВАТЕЛЕЙ*\\n\\n📊 Всего: {total_users:,}\\n🆕 Новые сегодня: {new_today}\\n📈 ARPU: {arpu:.1f} сом\\n📊 Конверсия в премиум: {conversion:.1f}%" 
        await update.message.reply_text(users, parse_mode="Markdown") 
 
    elif text == "⚙️ НАСТРОЙКИ": 
        settings = f"⚙️ *НАСТРОЙКИ СИСТЕМЫ*\\n\\n📊 Лимит бесплатных: {FREE_DAILY_LIMIT}\\n👨‍💼 Менеджер: {MANAGER_USERNAME}\\n👑 Владелец: {OWNER_ID}\\n📅 Дата запуска: {datetime.now().strftime('%Y-%m-%d')}" 
        await update.message.reply_text(settings, parse_mode="Markdown") 
 
    elif text == "📈 ГРАФИКИ": 
        await update.message.reply_text("📈 *Графики доступны в веб-панели*\\n\\nСсылка: http://artbazar.ai/admin", parse_mode="Markdown") 
 
    elif text == "🔄 СБРОС ЛИМИТОВ": 
        db = load_db() 
        for uid, user in db["users"].items(): 
            user["daily_used"] = 0 
        save_db(db) 
        await update.message.reply_text("✅ *Лимиты всех пользователей сброшены*", parse_mode="Markdown") 
 
    elif text == "📤 ЭКСПОРТ": 
        await update.message.reply_text("📤 *Экспорт данных в CSV*\\n\\nИспользуйте команду: /export users\\nИли: /export analytics", parse_mode="Markdown") 
 
# ==================== ОБЩИЕ ФУНКЦИИ ==================== 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    username = update.effective_user.username or "" 
 
    # Сохраняем username 
    user_data = get_user(user_id) 
    if username and not user_data.get("username"): 
        update_user(user_id, {"username": username}) 
 
    if user_id == OWNER_ID: 
        await show_owner_menu(update, user_id) 
    elif user_id in MANAGER_IDS: 
        await show_manager_menu(update, user_id) 
    else: 
        keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
        await update.message.reply_text("🌐 *ARTBAZAR AI*\\nВыберите язык:", parse_mode="Markdown", reply_markup=markup) 
 
async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    text = update.message.text 
 
    if text in ["🇷🇺 Русский", "🇰🇿 Қазақша", "🇰🇬 Кыргызча"]: 
        lang = {"🇷🇺 Русский": "RU", "🇰🇿 Қазақша": "KZ", "🇰🇬 Кыргызча": "KG"}[text] 
        update_user(user_id, {"lang": lang}) 
 
        if user_id == OWNER_ID: 
            await show_owner_menu(update, user_id) 
        elif user_id in MANAGER_IDS: 
            await show_manager_menu(update, user_id) 
        else: 
            await show_user_menu(update, user_id) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    text = update.message.text 
 
    # Определяем интерфейс в зависимости от роли 
    if user_id == OWNER_ID: 
        await owner_handle_message(update, context) 
    elif user_id in MANAGER_IDS: 
        await manager_handle_message(update, context) 
    else: 
        await user_handle_message(update, context) 
 
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    query = update.callback_query 
    await query.answer() 
 
    if query.data.startswith("premium_"): 
        months = {"premium_1": 1, "premium_6": 6, "premium_12": 12}[query.data] 
        price = {1: 499, 6: 1999, 12: 3499}[months] 
        await query.edit_message_text(f"💎 *Оформление ARTBAZAR PRO*\\n\\n📅 Срок: {months} месяц(ев)\\n💰 Стоимость: {price} сом\\n\\nОплата: {MANAGER_USERNAME}\\nПосле оплаты отправьте чек менеджеру", parse_mode="Markdown") 
 
async def limit_exceeded(update, user_id): 
    user = get_user(user_id) 
    text = f"❌ *ЛИМИТ ИСЧЕРПАН*\\n\\n📊 Использовано: {user['daily_used']}/3\\n🔄 Сброс через 24 часа\\n\\n💎 ARTBAZAR PRO открывает безлимит\\n👨‍💼 Менеджер: {MANAGER_USERNAME}" 
    await update.message.reply_text(text, parse_mode="Markdown") 
 
def main(): 
    logging.basicConfig(level=logging.INFO) 
    BOT_TOKEN = os.getenv("BOT_TOKEN") 
    if not BOT_TOKEN: 
        logging.error("No BOT_TOKEN") 
        return 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(CallbackQueryHandler(callback_handler)) 
    logging.info("🚀 ARTBAZAR AI запущен") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
