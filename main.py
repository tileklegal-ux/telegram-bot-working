import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Тексты для кнопок
MENU_TEXT = """🎨 *ARTBAZAR AI - Ваш AI-аналитик*

Что я умею:
• 🔍 Анализ товаров
• 📊 Профилирование ниш  
• 💰 Расчет маржи
• ❓ Помощь и обучение

Выберите действие:"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    
    # Создаем inline-клавиатуру
    keyboard = [
        [InlineKeyboardButton("🔍 Анализ товара", callback_data="analyze")],
        [InlineKeyboardButton("📊 Профиль ниши", callback_data="profile")],
        [InlineKeyboardButton("💰 Расчет маржи", callback_data="margin")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        MENU_TEXT,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий inline-кнопок"""
    query = update.callback_query
    await query.answer()  # Убираем "часики" на кнопке
    
    # Определяем ответ в зависимости от нажатой кнопки
    if query.data == "analyze":
        response = """🔍 *Анализ товара*

Я помогу проанализировать любой товар:
• Определю спрос и тренды
• Проанализирую конкурентов
• Рассчитаю потенциал продаж
• Дам рекомендации по цене

*Как использовать:*
1. Пришлите ссылку на товар
2. Или название товара
3. Я проведу полный анализ"""
        
    elif query.data == "profile":
        response = """📊 *Профилирование ниши*

Я создам детальный профиль ниши:
• Анализ рынка и объемов
• Изучение целевой аудитории
• Выявление ключевых игроков
• Определение точек роста

*Готов начать?*
Опишите нишу или пришлите ключевые слова"""
        
    elif query.data == "margin":
        response = """💰 *Расчет маржи*

Рассчитаю точную маржинальность:
• Себестоимость товара
• Логистика и накладные расходы
• Комиссии площадок
• Чистая прибыль

*Для расчета пришлите:*
1. Стоимость закупки
2. Цену продажи
3. Дополнительные расходы"""
        
    elif query.data == "help":
        response = """❓ *Помощь*

*Основные команды:*
/start - показать главное меню

*Как работает ARTBAZAR AI:*
1. Выберите нужную функцию
2. Следуйте инструкциям
3. Получите детальный анализ

*Поддержка:*
По вопросам работы бота обращайтесь к разработчикам.

🎯 *Совет:* Используйте официальный клиент Telegram для лучшего опыта."""
    
    else:
        response = "Неизвестная команда"
    
    # Обновляем сообщение с новым текстом и той же клавиатурой
    keyboard = [
        [InlineKeyboardButton("🔍 Анализ товара", callback_data="analyze")],
        [InlineKeyboardButton("📊 Профиль ниши", callback_data="profile")],
        [InlineKeyboardButton("💰 Расчет маржи", callback_data="margin")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    await query.edit_message_text(
        text=response,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def main():
    """Основная функция запуска бота"""
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logging.info("🤖 ARTBAZAR AI запускается...")
    app.run_polling()

if __name__ == "__main__":
    main()