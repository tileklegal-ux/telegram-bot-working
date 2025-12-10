import os 
import json 
import logging 
import random 
import asyncio 
from datetime import datetime 
from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
 
# ==================== КОНФИГУРАЦИЯ ==================== 
OWNER_ID = 1974482384 
MANAGER_ID = 571499876  
MANAGER_USERNAME = "@artbazar_manager" 
FREE_DAILY_LIMIT = 3 
 
# OpenAI конфигурация 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") 
OPENAI_MODEL = "gpt-3.5-turbo" 
 
# Проверяем наличие ключа OpenAI 
if OPENAI_API_KEY: 
    try: 
        import openai 
        openai.api_key = OPENAI_API_KEY 
        HAS_OPENAI = True 
        logging.info("✅ OpenAI подключен") 
    except ImportError: 
        HAS_OPENAI = False 
        logging.warning("❌ OpenAI библиотека не установлена") 
else: 
    HAS_OPENAI = False 
    logging.warning("❌ OPENAI_API_KEY не найден") 
 
# Рыночные данные для анализа 
MARKET_DATA = { 
    "Товары для животных": {"спрос": 200000, "конкуренция": 9, "маржа": 51, "сезон": "Март"}, 
    "Домашний текстиль": {"спрос": 319000, "конкуренция": 24, "маржа": 17, "сезон": "Ноябрь"}, 
    "Посуда": {"спрос": 415000, "конкуренция": 9, "маржа": 45, "сезон": "Круглый год"}, 
    "Детские товары": {"спрос": 830000, "конкуренция": 19, "маржа": 5, "сезон": "Круглый год"}, 
    "Спорт товары": {"спрос": 89000, "конкуренция": 12, "маржа": 45, "сезон": "Ноябрь"}, 
    "Красота и здоровье": {"спрос": 155000, "конкуренция": 6, "маржа": 92, "сезон": "Круглый год"}, 
    "Хоз. товары": {"спрос": 112000, "конкуренция": 13, "маржа": 110, "сезон": "Февраль"} 
} 
 
# ==================== OPENAI ФУНКЦИИ ==================== 
def get_openai_client(): 
    if not HAS_OPENAI: 
        return None 
    try: 
        return openai 
    except: 
        return None 
 
async def analyze_with_openai(product_name, analysis_type="product"): 
    client = get_openai_client() 
    if not client: 
        return await get_fallback_analysis(product_name, analysis_type) 
 
    try: 
        if analysis_type == "product": 
            prompt = f"Проанализируй товар '{product_name}' для онлайн-бизнеса. Ответь коротко." 
        else:  
            prompt = f"Проанализируй нишу '{product_name}' для e-commerce. Ответь коротко." 
 
        loop = asyncio.get_event_loop() 
        response = await loop.run_in_executor( 
            None, 
            lambda: client.ChatCompletion.create( 
                model=OPENAI_MODEL, 
                messages=[ 
                    {"role": "system", "content": "Ты бизнес-аналитик ARTBAZAR AI."}, 
                    {"role": "user", "content": prompt} 
                ], 
                temperature=0.7, 
                max_tokens=300 
            ) 
        ) 
 
        analysis = response.choices[0].message.content 
        return format_ai_response(analysis, analysis_type, product_name) 
 
    except Exception as e: 
        logging.error(f"OpenAI ошибка: {e}") 
        return await get_fallback_analysis(product_name, analysis_type) 
 
def format_ai_response(text, analysis_type, product_name): 
    if analysis_type == "product": 
        return f"🎯 *ARTBAZAR AI: СКРИНИНГ ТОВАРА*\\n\\n🏷 Товар: {product_name}\\n\\n{text}\\n\\n🤖 *Анализ выполнен с OpenAI*" 
    else: 
        return f"📈 *ARTBAZAR AI: ПРОФИЛЬ НИШИ*\\n\\n🏷 Ниша: {product_name}\\n\\n{text}\\n\\n🤖 *Анализ выполнен с OpenAI*" 
 
async def get_fallback_analysis(product_name, analysis_type): 
    if analysis_type == "product": 
        niche = random.choice(list(MARKET_DATA.keys())) 
        data = MARKET_DATA[niche] 
        demand = random.randint(50000, 500000) 
        competition = random.randint(5, 50) 
        margin = random.randint(25, 70) 
        return f"🎯 *ARTBAZAR AI: СКРИНИНГ ТОВАРА*\\n\\n🏷 Товар: {product_name}\\n📊 Ниша: {niche}\\n📈 Спрос: {demand:,}/мес\\n⚡ Конкуренция: {competition}/100\\n💰 Маржа: {margin}%\\n👥 Аудитория: 25-45 лет\\n🛒 Каналы: Маркетплейсы, соцсети\\n\\n🎯 Рекомендация: {'✅ Перспективный' if margin > 40 else '⚠️ Требует анализа'}\\n\\n⚠️ *Используется локальный анализ*" 
    else: 
        if product_name in MARKET_DATA: 
            data = MARKET_DATA[product_name] 
            return f"📈 *ARTBAZAR AI: ПРОФИЛЬ НИШИ*\\n\\n🏷 Ниша: {product_name}\\n📊 Спрос: {data['спрос']:,}/мес\\n⚡ Конкуренция: {data['конкуренция']}/100\\n💰 Маржа: {data['маржа']}%\\n📅 Сезон: {data['сезон']}\\n📊 Тренды: Рост онлайн-продаж\\n\\n🎯 Рекомендация: {'✅ Рекомендуем' if data['маржа'] > 30 else '⚠️ Требует анализа'}\\n\\n⚠️ *Используется локальный анализ*" 
        return f"❌ Ниша '{product_name}' не найдена\\n\\nДоступные ниши:\\n" + "\\n".join([f"• {n}" for n in MARKET_DATA.keys()]) 
 
async def analyze_margin_with_ai(cost, price): 
    profit = price - cost 
    margin = (profit / price) * 100 
    roi = (profit / cost) * 100 
 
    ai_advice = "" 
    client = get_openai_client() 
    if client: 
        try: 
            prompt = f"Товар: себестоимость {cost} ₸, цена {price} ₸. Маржа {margin:.1f}%, ROI {roi:.1f}%. Дай рекомендацию." 
            loop = asyncio.get_event_loop() 
            response = await loop.run_in_executor( 
                None, 
                lambda: client.ChatCompletion.create( 
                    model=OPENAI_MODEL, 
                    messages=[ 
                        {"role": "system", "content": "Ты финансовый консультант."}, 
                        {"role": "user", "content": prompt} 
                    ], 
                    temperature=0.7, 
                    max_tokens=100 
                ) 
            ) 
            ai_advice = response.choices[0].message.content 
        except: 
            ai_advice = "Проанализируйте цены конкурентов." 
 
    result = f"🧮 *ARTBAZAR AI: МАРЖИНАЛЬНЫЙ АНАЛИЗ*\\n\\n📦 Себестоимость: {cost:,.0f} ₸\\n💰 Цена: {price:,.0f} ₸\\n💵 Прибыль: {profit:,.0f} ₸\\n📊 Маржа: {margin:.1f}%\\n🚀 ROI: {roi:.1f}%\\n\\n{'✅ Рентабельно' if margin > 30 else '⚠️ Низкая маржа'}" 
 
    if ai_advice: 
        result += f"\\n\\n💡 *AI-рекомендация:* {ai_advice}" 
        if HAS_OPENAI: 
            result += "\\n🤖 *С OpenAI*" 
 
    return result 
 
# ==================== БАЗА ДАННЫХ ==================== 
def load_db(): 
    try: 
        with open("artbazar_db.json", "r", encoding="utf-8") as f: 
            return json.load(f) 
    except: 
        return {"users": {}, "analytics": 0, "revenue": 0, "premium_users": [], "ai_analytics": 0} 
 
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
            "total_analytics": 0, 
            "username": "", 
            "first_name": "", 
            "is_premium": False, 
            "ai_used": 0 
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
 
def increment_ai_analytics(): 
    db = load_db() 
    db["ai_analytics"] = db.get("ai_analytics", 0) + 1 
    save_db(db) 
 
def check_limit(user_id): 
    user = get_user(user_id) 
    today = datetime.now().strftime("%Y-%m-%d") 
    if user["last_reset"] != today: 
        user["daily_used"] = 0 
        user["last_reset"] = today 
        update_user(user_id, user) 
    if user.get("is_premium"): 
        return True 
 
def use_analysis(user_id, is_ai=False): 
    user = get_user(user_id) 
    user["daily_used"] += 1 
    user["total_analytics"] += 1 
    if is_ai: 
        user["ai_used"] = user.get("ai_used", 0) + 1 
        increment_ai_analytics() 
    update_user(user_id, user) 
    db = load_db() 
    db["analytics"] = db.get("analytics", 0) + 1 
    save_db(db) 
 
# ==================== ИНТЕРФЕЙС ВЛАДЕЛЬЦА ==================== 
async def show_owner_panel(update, user_id): 
    db = load_db() 
    ai_status = "✅ Активен" if HAS_OPENAI else "❌ Отключен" 
    text = f"👑 *ARTBAZAR AI - БИЗНЕС ПАНЕЛЬ*\\n\\n👥 Пользователи: {len(db['users']):,}\\n📊 Анализов: {db.get('analytics', 0):,}\\n🤖 AI-анализов: {db.get('ai_analytics', 0):,}\\n🧠 OpenAI: {ai_status}\\n💰 Выручка: {db.get('revenue', 0):,} сом" 
    keyboard = [ 
        ["📊 Статистика", "💰 Финансы"], 
        ["👥 Пользователи", "⚙️ Настройки"], 
        ["⬅️ К пользователю"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup) 
 
async def handle_owner_command(update, text, user_id): 
    db = load_db() 
 
    if text == "📊 Статистика": 
        ai_status = "✅ Подключен" if HAS_OPENAI else "❌ Не подключен" 
        stats = f"📊 *СТАТИСТИКА СИСТЕМЫ*\\n\\n👥 Пользователей: {len(db['users']):,}\\n📊 Анализов: {db.get('analytics', 0):,}\\n🤖 AI-анализов: {db.get('ai_analytics', 0):,}\\n🧠 OpenAI: {ai_status}\\n💰 Выручка: {db.get('revenue', 0):,} сом\\n📅 Дата: {datetime.now().strftime('%%d.%%m.%%Y %%H:%%M')}" 
        await update.message.reply_text(stats, parse_mode="Markdown") 
 
    elif text == "💰 Финансы": 
        ai_cost = db.get('ai_analytics', 0) * 0.002 
        finance = f"💰 *ФИНАНСОВАЯ АНАЛИТИКА*\\n\\n💵 Общая выручка: {db.get('revenue', 0):,} сом\\n📊 Средний чек: 499 сом\\n💎 Премиум подписок: {len(db.get('premium_users', []))}\\n🤖 Затраты на AI: {ai_cost:.2f}$\\n📈 Целевая выручка: 50,000 сом" 
        await update.message.reply_text(finance, parse_mode="Markdown") 
 
    elif text == "👥 Пользователи": 
        users_count = len(db["users"]) 
        # Простой подсчет активных пользователей 
        active_users = 0 
        for u in db["users"].values(): 
            if u.get("total_analytics", 0) 
                active_users += 1 
        # Простой подсчет AI пользователей 
        ai_users = 0 
        for u in db["users"].values(): 
            if u.get("ai_used", 0) 
                ai_users += 1 
        users = f"👥 *АНАЛИТИКА ПОЛЬЗОВАТЕЛЕЙ*\\n\\n📊 Всего пользователей: {users_count:,}\\n📈 Активных пользователей: {active_users}\\n🤖 Пользователей AI: {ai_users}\\n📊 Конверсия: {(active_users/max(1, users_count))*100:.1f}%%" 
        await update.message.reply_text(users, parse_mode="Markdown") 
 
    elif text == "⚙️ Настройки": 
        ai_status = "✅ Подключен" if HAS_OPENAI else "❌ Не подключен (добавьте OPENAI_API_KEY)" 
        settings = f"⚙️ *НАСТРОЙКИ СИСТЕМЫ*\\n\\n📊 Лимит бесплатных: {FREE_DAILY_LIMIT}\\n👨‍💼 Менеджер: @artbazar_support\\n👑 Владелец: {OWNER_ID}\\n🤖 OpenAI модель: {OPENAI_MODEL}\\n🔑 OpenAI статус: {ai_status}" 
        await update.message.reply_text(settings, parse_mode="Markdown") 
 
    elif text == "⬅️ К пользователю": 
        await show_user_menu(update, user_id) 
 
# ==================== ИНТЕРФЕЙС МЕНЕДЖЕРА ==================== 
async def show_manager_panel(update, user_id): 
    db = load_db() 
    ai_status = "✅ Активен" if HAS_OPENAI else "⚠️ Локальный" 
    text = f"👨‍💼 *ARTBAZAR AI - МЕНЕДЖЕР ПАНЕЛЬ*\\n\\n👥 Пользователи: {len(db['users']):,}\\n📊 Анализов: {db.get('analytics', 0):,}\\n🤖 AI-анализов: {db.get('ai_analytics', 0):,}\\n🧠 Режим: {ai_status}\\n💰 Выручка: {db.get('revenue', 0):,} сом" 
    keyboard = [ 
        ["📊 СТАТИСТИКА", "👥 ПОЛЬЗОВАТЕЛИ"], 
        ["💎 ПРЕМИУМ", "📈 АНАЛИТИКА"], 
        ["⬅️ К пользователю"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup) 
 
async def handle_manager_command(update, text, user_id): 
    db = load_db() 
 
    if text == "📊 СТАТИСТИКА": 
        stats = f"📊 *СТАТИСТИКА*\\n\\n👥 Пользователей: {len(db['users']):,}\\n📊 Анализов: {db.get('analytics', 0):,}\\n🤖 AI-анализов: {db.get('ai_analytics', 0):,}\\n💰 Выручка: {db.get('revenue', 0):,} сом\\n📅 Дата: {datetime.now().strftime('%%d.%%m.%%Y %%H:%%M')}" 
        await update.message.reply_text(stats, parse_mode="Markdown") 
 
    elif text == "👥 ПОЛЬЗОВАТЕЛИ": 
        recent_users = [] 
        user_items = list(db["users"].items()) 
        if len(user_items) 
            user_items = user_items[-5:] 
        for uid, user in user_items: 
            name = user.get("first_name", "Пользователь") 
            ai = f" (🤖{user.get('ai_used', 0)})" if user.get("ai_used", 0)  else "" 
            recent_users.append(f"• {name} - {user.get('total_analytics', 0)} анализ{ai}") 
        users = f"👥 *ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ*\\n\\n" + "\\n".join(recent_users) + f"\\n\\n📊 Всего: {len(db['users']):,}" 
        await update.message.reply_text(users, parse_mode="Markdown") 
 
    elif text == "💎 ПРЕМИУМ": 
        premium = f"💎 *УПРАВЛЕНИЕ ПРЕМИУМ*\\n\\n👤 Премиум пользователей: {len(db.get('premium_users', []))}\\n💰 Тарифы:\\n- 1 месяц: 499 сом\\n- 6 месяцев: 1999 сом\\n- 1 год: 3499 сом\\n🤖 AI-анализы: {'✅ Включены' if HAS_OPENAI else '⚠️ Локальные'}\\n\\n📞 Для активации: /premium user_id" 
        await update.message.reply_text(premium, parse_mode="Markdown") 
 
    elif text == "📈 АНАЛИТИКА": 
        top_users = [] 
        for uid, user in db["users"].items(): 
            top_users.append((uid, user.get("total_analytics", 0), user.get("ai_used", 0))) 
        top_users.sort(key=lambda x: x[1], reverse=True) 
        top5 = top_users[:3] if len(top_users)  else top_users 
        analytics = f"📈 *АНАЛИТИКА АКТИВНОСТИ*\\n\\nТоп активных пользователей:\\n" 
        for i, (uid, count, ai_count) in enumerate(top5, 1): 
            ai = f" (🤖{ai_count})" if ai_count  else "" 
            analytics += f"{i}. ID: {uid[:8]}... - {count} анализ{ai}\\n" 
        analytics += f"\\n📊 Всего анализов: {db.get('analytics', 0):,}\\n🤖 AI-анализов: {db.get('ai_analytics', 0):,}" 
        await update.message.reply_text(analytics, parse_mode="Markdown") 
 
    elif text == "⬅️ К пользователю": 
        await show_user_menu(update, user_id) 
 
# ==================== ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ ==================== 
async def show_user_menu(update, user_id): 
    user = get_user(user_id) 
    premium_status = "💎 PRO" if user.get("is_premium") else "👤 БАЗОВЫЙ" 
    ai_status = "🤖 AI доступен" if HAS_OPENAI else "⚠️ Локальный анализ" 
    menu_text = f"🎯 *ARTBAZAR AI - БИЗНЕС АНАЛИТИК*\\n\\n📊 Статус: {premium_status}\\n📈 Анализов сегодня: {user['daily_used']}/{FREE_DAILY_LIMIT}\\n🤖 AI-анализов: {user.get('ai_used', 0)}\\n🧠 Режим: {ai_status}\\n\\nВыберите опцию:" 
    keyboard = [ 
        ["🚀 СКРИНИНГ ТОВАРА", "📈 ПРОФИЛЬ НИШИ"], 
        ["💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ", "💎 ARTBAZAR PRO"], 
        ["🌐 ЯЗЫК", "❓ ПОМОЩЬ"] 
    ] 
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=markup) 
 
async def handle_user_command(update, text, user_id, context): 
 
    if text == "🚀 СКРИНИНГ ТОВАРА": 
        if check_limit(user_id): 
            ai_note = "🤖 *Анализ выполняется с помощью OpenAI*" if HAS_OPENAI else "⚠️ *Используется локальный анализ*" 
            await update.message.reply_text(f"🎯 *Введите название товара для AI-скрининга*\\n\\nПример: Умная колонка Яндекс Станция\\n\\n{ai_note}", parse_mode="Markdown") 
            context.user_data["awaiting_product"] = True 
        else: 
            await limit_exceeded(update, user_id) 
 
    elif text == "📈 ПРОФИЛЬ НИШИ": 
        if check_limit(user_id): 
            ai_note = "🤖 *Анализ выполняется с помощью OpenAI*" if HAS_OPENAI else "⚠️ *Используется локальный анализ*" 
            niches = "\\n".join([f"• {n}" for n in MARKET_DATA.keys()]) 
            await update.message.reply_text(f"📊 *Выберите нишу:*\\n\\n{niches}\\n\\n{ai_note}", parse_mode="Markdown") 
            context.user_data["awaiting_niche"] = True 
        else: 
            await limit_exceeded(update, user_id) 
 
    elif text == "💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ": 
        ai_note = "🤖 *С AI-рекомендациями*" if HAS_OPENAI else "" 
        await update.message.reply_text(f"🧮 *Введите данные:*\\n\\nСебестоимость | Цена\\n\\nПример: 5000 | 8000\\n\\n{ai_note}", parse_mode="Markdown") 
        context.user_data["awaiting_margin"] = True 
 
    elif text == "💎 ARTBAZAR PRO": 
        ai_feature = "🤖 Полный доступ к OpenAI GPT" if HAS_OPENAI else "🤖 Расширенный локальный анализ" 
        premium_text = f"💎 *ARTBAZAR PRO*\\n\\n✅ Безлимитные анализы\\n✅ Расширенные отчеты\\n✅ Приоритетная поддержка\\n✅ Экспорт в Excel\\n{ai_feature}\\n\\n💰 Тарифы:\\n1 месяц - 499 сом\\n6 месяцев - 1999 сом\\n1 год - 3499 сом\\n\\n👨‍💼 Менеджер: @artbazar_support" 
        await update.message.reply_text(premium_text, parse_mode="Markdown") 
 
    elif text == "🌐 ЯЗЫК": 
        keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча", "⬅️ Назад"]] 
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
        await update.message.reply_text("🌐 *Выберите язык:*", parse_mode="Markdown", reply_markup=markup) 
 
    elif text == "❓ ПОМОЩЬ": 
        ai_info = "🤖 Бот использует OpenAI GPT для анализа" if HAS_OPENAI else "⚠️ Бот использует локальную базу для анализа" 
        help_text = f"❓ *ARTBAZAR AI - ПОМОЩЬ*\\n\\n🚀 СКРИНИНГ ТОВАРА - AI-анализ товара\\n📈 ПРОФИЛЬ НИШИ - аналитика рынка\\n💰 МАРЖИНАЛЬНЫЙ АНАЛИЗ - расчет с рекомендациями\\n💎 ARTBAZAR PRO - премиум доступ\\n{ai_info}\\n\\n📞 Поддержка: @artbazar_support" 
        await update.message.reply_text(help_text, parse_mode="Markdown") 
 
    elif text == "⬅️ Назад": 
        await show_user_menu(update, user_id) 
 
    elif text in ["🇷🇺 Русский", "🇰🇿 Қазақша", "🇰🇬 Кыргызча"]: 
        await update.message.reply_text(f"✅ Язык изменен на {text}", parse_mode="Markdown") 
        await show_user_menu(update, user_id) 
 
# ==================== ОСНОВНЫЕ ОБРАБОТЧИКИ ==================== 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    first_name = update.effective_user.first_name or "" 
    username = update.effective_user.username or "" 
 
    update_user(user_id, {"first_name": first_name, "username": username}) 
 
    if user_id == OWNER_ID: 
        await show_owner_panel(update, user_id) 
    elif user_id == MANAGER_ID: 
        await show_manager_panel(update, user_id) 
    else: 
        ai_note = "🤖 *Бот работает на OpenAI GPT*" if HAS_OPENAI else "📊 *Бот использует локальную базу данных*" 
        keyboard = [["🇷🇺 Русский", "🇰🇿 Қазақша"], ["🇰🇬 Кыргызча"]] 
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
        await update.message.reply_text(f"🌐 *ARTBAZAR AI*\\nВыберите язык:\\n\\n{ai_note}", parse_mode="Markdown", reply_markup=markup) 
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id 
    text = update.message.text 
 
    # Обработка анализов 
    if context.user_data.get("awaiting_product"): 
        if check_limit(user_id): 
            if HAS_OPENAI: 
                await update.message.reply_text("🤖 *AI анализирует товар...*", parse_mode="Markdown") 
            else: 
                await update.message.reply_text("📊 *Анализируем товар...*", parse_mode="Markdown") 
            analysis = await analyze_with_openai(text, "product") 
            use_analysis(user_id, is_ai=HAS_OPENAI) 
            await update.message.reply_text(analysis, parse_mode="Markdown") 
        else: 
            await limit_exceeded(update, user_id) 
        context.user_data["awaiting_product"] = False 
        return 
 
    elif context.user_data.get("awaiting_niche"): 
        if check_limit(user_id): 
            if HAS_OPENAI: 
                await update.message.reply_text("🤖 *AI анализирует нишу...*", parse_mode="Markdown") 
            else: 
                await update.message.reply_text("📊 *Анализируем нишу...*", parse_mode="Markdown") 
            analysis = await analyze_with_openai(text, "niche") 
            use_analysis(user_id, is_ai=HAS_OPENAI) 
            await update.message.reply_text(analysis, parse_mode="Markdown") 
        else: 
            await limit_exceeded(update, user_id) 
        context.user_data["awaiting_niche"] = False 
        return 
 
    elif context.user_data.get("awaiting_margin"): 
        try: 
            cost, price = [float(x.strip()) for x in text.split("|")] 
            if HAS_OPENAI: 
                await update.message.reply_text("🤖 *AI готовит рекомендации...*", parse_mode="Markdown") 
            analysis = await analyze_margin_with_ai(cost, price) 
            use_analysis(user_id, is_ai=HAS_OPENAI) 
            await update.message.reply_text(analysis, parse_mode="Markdown") 
        except: 
            await update.message.reply_text("❌ *Ошибка формата*\\nПример: 5000 | 8000", parse_mode="Markdown") 
        context.user_data["awaiting_margin"] = False 
        return 
 
    # Определяем роль 
    if user_id == OWNER_ID: 
        await handle_owner_command(update, text, user_id) 
    elif user_id == MANAGER_ID: 
        await handle_manager_command(update, text, user_id) 
    else: 
        await handle_user_command(update, text, user_id, context) 
 
async def limit_exceeded(update, user_id): 
    user = get_user(user_id) 
    text = f"❌ *ЛИМИТ ИСЧЕРПАН*\\n\\n📊 Использовано: {user['daily_used']}/{FREE_DAILY_LIMIT}\\n🔄 Сброс через 24 часа\\n\\n💎 ARTBAZAR PRO открывает безлимитный доступ\\n👨‍💼 Менеджер: @artbazar_support" 
    await update.message.reply_text(text, parse_mode="Markdown") 
 
def main(): 
    logging.basicConfig(level=logging.INFO) 
    BOT_TOKEN = os.getenv("BOT_TOKEN") 
    if not BOT_TOKEN: 
        logging.error("❌ No BOT_TOKEN") 
        return 
 
    if HAS_OPENAI: 
        logging.info("✅ OpenAI подключен") 
    else: 
        logging.warning("⚠️ OpenAI не подключен - используется локальный анализ") 
 
    app = Application.builder().token(BOT_TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    logging.info(f"🚀 ARTBAZAR AI запущен {'с OpenAI' if HAS_OPENAI else 'в локальном режиме'}") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
