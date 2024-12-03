from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import difflib
import logging

# Настройка логгирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Хранение текстов для сравнения
texts = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("\U0001F195 Новый текст"), KeyboardButton("\u2139\ufe0f Помощь")],
        [KeyboardButton("\U0001F504 Сброс"), KeyboardButton("\U0001F4DD История")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "\U0001F44B *Привет!*\n\n"
        "Отправь мне два текста по очереди, и я покажу, чем они отличаются. "
        "Используй кнопки ниже для управления.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\u2139\ufe0f *Помощь:*\n\n"
        "1. Нажмите \U0001F195 \"Новый текст\", чтобы начать.\n"
        "2. Отправьте два текста по очереди для сравнения.\n"
        "3. Используйте \U0001F504 \"Сброс\", чтобы очистить данные.\n"
        "4. Нажмите \U0001F4DD \"История\", чтобы увидеть последние сравнения.",
        parse_mode="Markdown"
    )

# Сброс текстов
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texts.pop(user_id, None)  # Удаляем данные пользователя, если они есть
    await update.message.reply_text("\U0001F504 Данные сброшены. Начните заново, отправив \U0001F195 \"Новый текст\".")

# История сравнений
history = {}

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_history = history.get(user_id, [])

    if user_history:
        response = "\U0001F4DD *История сравнений:*\n\n"
        response += "\n".join(user_history[-5:])  # Показываем последние 5 сравнений
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("\U0001F4DD История пуста. Отправьте тексты для сравнения.")

# Обработка текстов
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Проверяем, что текст не пустой
    if not text.strip():
        await update.message.reply_text("\u2757 Текст не может быть пустым. Пожалуйста, отправьте текст.")
        return

    if text == "\U0001F504 Сброс":
        await reset(update, context)
        return
    elif text == "\u2139\ufe0f Помощь":
        await help_command(update, context)
        return
    elif text == "\U0001F4DD История":
        await show_history(update, context)
        return

    # Сохранение и сравнение текстов
    if user_id not in texts:
        texts[user_id] = [text]
        await update.message.reply_text("\u2705 Первый текст сохранен. Теперь отправьте второй текст.")
    elif len(texts[user_id]) == 1:
        texts[user_id].append(text)
        differences = compare_texts(texts[user_id][0], texts[user_id][1])

        if differences.strip():
            response = f"\U0001F50E *Различия между текстами:*\n\n{differences}"
        else:
            response = "\U0001F389 Тексты полностью совпадают!"

        await update.message.reply_text(response, parse_mode="HTML")

        # Сохраняем в историю
        if user_id not in history:
            history[user_id] = []
        history[user_id].append(response)

        # Предлагаем начать заново
        keyboard = [
            [KeyboardButton("\U0001F195 Новый текст"), KeyboardButton("\u2139\ufe0f Помощь")],
            [KeyboardButton("\U0001F504 Сброс"), KeyboardButton("\U0001F4DD История")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Вы можете начать заново, отправив новый текст или получить помощь.",
            reply_markup=reply_markup
        )

        texts.pop(user_id)  # Очистка данных после сравнения
    else:
        await update.message.reply_text("\u2757 Что-то пошло не так. Напишите \U0001F504 \"Сброс\", чтобы начать заново.")

# Сравнение текстов с подчеркиванием различий
def compare_texts(text1, text2):
    diff = difflib.ndiff(text1.splitlines(), text2.splitlines())
    result = []
    for line in diff:
        if line.startswith("- "):
            result.append(f"Удалено: {line[2:]}\n")
        elif line.startswith("+ "):
            result.append(f"Добавлено: {line[2:]}\n")
        elif line.startswith("  "):
            result.append(f"{line[2:]}\n")
    return "".join(result).strip() or "Тексты совпадают или не содержат различий."

# Основная функция
def main():
    app = Application.builder().token("7709470340:AAH3M8YTcub5-6zUO0rOr6TwJloF448DjsE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("history", show_history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

