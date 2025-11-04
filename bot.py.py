from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === Настройки ===
TOKEN = "8382680359:AAE20pQe6HbCRmkqm9S1PYruaHBpX7rK3Co"

# Состояния пользователей
user_data = {}

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"state": "waiting_first"}
    await update.message.reply_text("📥 Пришлите основной список (я сам выделю 10-значные ID).")

# === Обработка сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if not text:
        return

    state = user_data.get(chat_id, {}).get("state")

    # --- Получение первого списка
    if state == "waiting_first":
        ids1 = extract_ten_digit_ids(text)
        if not ids1:
            await update.message.reply_text("⚠️ Не найдено ни одного 10-значного ID. Пришлите заново.")
            return
        user_data[chat_id] = {"state": "waiting_second", "list1": ids1}
        await update.message.reply_text(f"✅ Принято {len(ids1)} ID.\nТеперь пришлите список для исключения.")
        return

    # --- Получение второго списка
    if state == "waiting_second":
        ids2 = extract_ten_digit_ids(text)
        if not ids2:
            await update.message.reply_text("⚠️ Во втором списке нет 10-значных ID. Пришлите заново.")
            return

        ids1 = user_data[chat_id].get("list1", [])
        result = [x for x in ids1 if x not in ids2]

        del user_data[chat_id]

        if not result:
            await update.message.reply_text("✅ Все ID были исключены. Остаток пуст.")
        else:
            await update.message.reply_text(f"✅ Осталось {len(result)} ID:")
            # Отправляем по частям, если их много
            for i in range(0, len(result), 100):
                await update.message.reply_text("\n".join(result[i:i+100]))

            await update.message.reply_text("🔄 Отправьте /start, чтобы начать заново.")
        return

    # --- Если ничего не выбрано
    await update.message.reply_text("🔹 Отправьте /start, чтобы начать.")


def extract_ten_digit_ids(text):
    import re
    ids = re.findall(r"\b\d{10}\b", text)
    return list(dict.fromkeys(ids))  # Убираем дубли


# === Запуск ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
