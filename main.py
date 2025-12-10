import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем обе клавиатуры: Reply и Inline"""
    
    # 1. ReplyKeyboardMarkup (для официальных клиентов)
    reply_keyboard = [["ANALYZE", "PROFILE"], ["MARGIN", "HELP"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    # 2. InlineKeyboardMarkup (для всех клиентов)
    inline_keyboard = [
        [InlineKeyboardButton("🔍 ANALYZE", callback_data="analyze")],
        [InlineKeyboardButton("📊 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("💰 MARGIN", callback_data="margin")],
        [InlineKeyboardButton("❓ HELP", callback_data="help")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    await update.message.reply_text(
        "🎨 *ARTBAZAR AI*\n\n"
        "Выберите действие:\n\n"
        "📱 **Для официального Telegram:**\n"
        "Клавиатура появится ниже\n\n"
        "📲 **Для других клиентов:**\n"
        "Используйте кнопки в сообщении",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    # Отправляем inline клавиатуру отдельно
    await update.message.reply_text(
        "Или выберите здесь:",
        reply_markup=inline_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline кнопок"""
    query = update.callback_query
    await query.answer()
    
    responses = {
        "analyze": "🔍 *Анализ продукта*\n\nФункция в разработке...",
        "profile": "📊 *Профилирование ниши*\n\nСкоро будет доступно!",
        "margin": "💰 *Расчет маржи*\n\nВ процессе разработки.",
        "help": "❓ *Помощь*\n\nИспользуйте команду /start\n\nОфициальный Telegram: https://telegram.org"
    }
    
    await query.edit_message_text(
        responses.get(query.data, "Неизвестная команда"),
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений от Reply клавиатуры"""
    text = update.message.text
    
    responses = {
        "ANALYZE": "🔍 Вы выбрали анализ продукта",
        "PROFILE": "📊 Вы выбрали профилирование ниши",
        "MARGIN": "💰 Вы выбрали расчет маржи",
        "HELP": "❓ Помощь: установите официальный Telegram"
    }
    
    if text in responses:
        await update.message.reply_text(responses[text])
    else:
        await update.message.reply_text(f"Вы написали: {text}")

def main():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    
    # Inline кнопки
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Текстовые сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()