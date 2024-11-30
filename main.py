import os
import sys
import signal
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import difflib

# Имя файла для хранения PID
PID_FILE = "bot.pid"

# Проверяем, запущен ли процесс
if os.path.exists(PID_FILE):
    with open(PID_FILE, "r") as f:
        existing_pid = int(f.read().strip())
    try:
        # Проверяем, работает ли процесс с этим PID
        os.kill(existing_pid, 0)
        print("Бот уже запущен! Завершение...")
        sys.exit()
    except OSError:
        # Если процесс с PID не найден, продолжаем работу
        print("Старый PID не активен. Удаляю файл...")
        os.remove(PID_FILE)

# Записываем текущий PID в файл
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

def clean_up():
    """Удаляет PID-файл при завершении работы"""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

# Настраиваем обработчик завершения процесса
signal.signal(signal.SIGINT, lambda signum, frame: sys.exit())
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit())

# Блок работы бота
try:
    print("Бот запущен!")

    # Основная логика бота
    # Хранение текстов для сравнения
    texts = {}

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [KeyboardButton("🆕 Новый текст"), KeyboardButton("ℹ️ Помощь")],
            [KeyboardButton("♻️ Сброс")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "👋 *Привет!*\n\n"
            "Отправь мне два текста по очереди, и я покажу, чем они отличаются. "
            "Используй кнопки ниже для управления.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id in texts:
            texts.pop(user_id)
        await update.message.reply_text("♻️ Данные сброшены. Вы можете начать сначала, отправив первый текст.")

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = update.message.text.strip()

        if text == "🆕 Новый текст" or text == "♻️ Сброс":
            await reset(update, context)
            return
        elif text == "ℹ️ Помощь":
            await show_help(update, context)
            return

        if user_id not in texts:
            texts[user_id] = [text]
            await update.message.reply_text("✅ Первый текст сохранен. Теперь отправьте второй текст.")
        elif len(texts[user_id]) == 1:
            texts[user_id].append(text)
            differences = compare_texts(texts[user_id][0], texts[user_id][1])

            if differences:
                await update.message.reply_text(
                    f"🔍 *Различия между текстами:*\n\n{differences}",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("🎉 Тексты полностью совпадают!")

            keyboard = [
                [KeyboardButton("🆕 Новый текст"), KeyboardButton("ℹ️ Помощь")],
                [KeyboardButton("♻️ Сброс")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Вы можете начать заново, отправив новый текст или получить помощь.",
                reply_markup=reply_markup
            )

            texts.pop(user_id)
        else:
            await update.message.reply_text("❗️ Произошла ошибка. Напишите /reset, чтобы начать заново.")

    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "ℹ️ *Помощь*\n\n"
            "Этот бот позволяет находить различия между двумя текстами. Вот как с ним работать:\n"
            "1️⃣ Отправьте первый текст.\n"
            "2️⃣ Отправьте второй текст.\n"
            "3️⃣ Бот покажет различия между текстами.\n\n"
            "Используйте кнопки для сброса или отправки новых текстов.",
            parse_mode="Markdown"
        )

    def compare_texts(text1, text2):
        diff = difflib.ndiff(text1, text2)
        result = []
        for i in diff:
            if i.startswith("- "):
                result.append(f"<u>{i[2:]}</u>")
            elif i.startswith("+ "):
                result.append(f"<u>{i[2:]}</u>")
            else:
                result.append(i[2:])
        return "".join(result) or "Тексты совпадают или не содержат различий."

    def main():
        app = Application.builder().token("7709470340:AAH3M8YTcub5-6zUO0rOr6TwJloF448DjsE").build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("reset", reset))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.run_polling(drop_pending_updates=True)

    if __name__ == "__main__":
        main()

except KeyboardInterrupt:
    print("Бот остановлен.")
finally:
    clean_up()