from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import difflib

# Хранение текстов для сравненияxx
texts = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🆕 Новый текст"), KeyboardButton("ℹ️ Помощь")],
        [KeyboardButton("🆕 Сброс")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "👋 *Привет!*\n\n"
        "Отправь мне два текста по очереди, и я покажу, чем они отличаются. "
        "Используйте кнопки ниже для управления.",
        parse_mode="Markdown",  # Используем Markdown
        reply_markup=reply_markup
    )

# Обработка текстов
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Проверяем, что текст не пустой
    if not text.strip():
        await update.message.reply_text("❗ Текст не может быть пустым. Пожалуйста, отправьте текст.")
        return

    if user_id not in texts:
        texts[user_id] = [text]
        await update.message.reply_text(
            "✅ Первый текст сохранен. Теперь отправьте второй текст."
        )
    elif len(texts[user_id]) == 1:
        texts[user_id].append(text)
        differences = compare_texts(texts[user_id][0], texts[user_id][1])

        if differences:
            await update.message.reply_text(
                f"🔍 *Различия между текстами:*\n\n{differences}",
                parse_mode="HTML"  # Используем HTML для разметки
            )
        else:
            await update.message.reply_text(
                "🎉 Тексты полностью совпадают!"
            )

        # Клавиатура с кнопками после сравнения
        keyboard = [
            [KeyboardButton("🆕 Новый текст"), KeyboardButton("ℹ️ Помощь")],
            [KeyboardButton("🆕 Сбросить")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        # Отправляем клавиатуру
        await update.message.reply_text(
            "Вы можете начать заново, отправив новый текст или получить помощь.",
            reply_markup=reply_markup
        )

        texts.pop(user_id)  # Очистка данных после сравнения
    else:
        await update.message.reply_text("❗ Что-то пошло не так. Напишите /reset, чтобы начать заново.")

# Сравнение текстов с подчеркиванием различийq
def compare_texts(text1, text2):
    diff = difflib.ndiff(text1, text2)
    result = []
    for i in diff:
        if i.startswith("- "):
            result.append(f"<u>{i[2:]}</u>")  # Подчеркиваем символы, которые есть только в первом тексте
        elif i.startswith("+ "):
            result.append(f"<u>{i[2:]}</u>")  # Подчеркиваем символы, которые есть только во втором тексте
        else:
            result.append(i[2:])
    return "".join(result) or "Тексты совпадают или не содержат различий."

# Основная функция
def main():
    app = Application.builder().token("7709470340:AAH3M8YTcub5-6zUO0rOr6TwJloF448DjsE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()