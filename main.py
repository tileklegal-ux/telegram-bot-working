import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с исправленной клавиатурой"""
    # Клавиатура 2x2
    keyboard = [
        ["🔍 ANALYZE PRODUCT", "📊 PROFILE NICHE"],
        ["💰 CALCULATE MARGIN", "❓ HELP"]
    ]
    
    # Создаем клавиатуру с правильными параметрами
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,        # Автоматически подгонять размер
        one_time_keyboard=False,     # Не скрывать после нажатия
        selective=False,             # Показывать всем в чате
        input_field_placeholder="Выберите действие"  # Подсказка в поле ввода
    )
    
    await update.message.reply_text(
        "🎨 *ARTBAZAR AI готов! Выберите действие:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_text = update.message.text
    
    # Убираем эмодзи для сравнения
    clean_text = user_text.replace("🔍 ", "").replace("📊 ", "").replace("💰 ", "").replace("❓ ", "")
    
    if clean_text in ["ANALYZE PRODUCT", "PROFILE NICHE", "CALCULATE MARGIN", "HELP"]:
        logging.info(f"User pressed button: {clean_text}")
        
        # Добавляем простые ответы для каждой кнопки
        responses = {
            "ANALYZE PRODUCT": "🔍 *Анализ продукта*\n\nЭта функция скоро будет доступна!",
            "PROFILE NICHE": "📊 *Профилирование ниши*\n\nРабота над функцией в процессе...",
            "CALCULATE MARGIN": "💰 *Расчет маржи*\n\nФункция калькулятора в разработке.",
            "HELP": "❓ *Помощь*\n\nДоступные команды:\n• /start - показать клавиатуру\n\nКнопки:\n• 🔍 Анализ продукта\n• 📊 Профилирование ниши\n• 💰 Расчет маржи\n• ❓ Помощь"
        }
        
        await update.message.reply_text(
            responses.get(clean_text, f"Вы выбрали: {clean_text}"),
            parse_mode="Markdown"
        )
        return
    
    # Если не нажатие кнопки, просто отвечаем
    await update.message.reply_text(f"Вы написали: {user_text}")

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logging.info("🤖 Бот запускается...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Игнорировать сообщения во время простоя
    )

if __name__ == "__main__":
    main()