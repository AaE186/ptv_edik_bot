from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
import asyncio

# ======== СПИСОК ПОЛЬЗОВАТЕЛЕЙ =========
target_users = {
    "all": [
        "@nknwn86", "@r_shrlv", "@miiglluna", "@Linzhy13", "@Ikc0ta", "@derlegen",
        "@Friderico_dourden", "@maximoffn", "@astor602", "@Nastya_Kosukhina",
        "@moarit", "@vladysham", "@by_gelechka", "@Maksimon777", "@alexa_vasyaeva",
        '@yvslk', "@merkovi", "@nastya3_56", "@yulshhhh", "@poliana_aa", "@Alkvlo",
        "@ssorelss", "@min_sai", "@Tuturukhekhe", "@marieta_v7", "@b1ack_dah1ia",
        "@speculum_59", "@D1am0nd_30", "@fjggkfg", "@Lancer_999", "@aa1esya",
    ],
    "photo": ["@miiglluna", "@derlegen", "@FLYINGeyesOFFICIAL21"],
    "designer": ["@Ikc0ta", "@maximoffn"],
    "copy": ["@alexa_vasyaeva", "@astor602", "aaaaa"],
    "video": ["@Friderico_dourden", "@r_shrlv"],
    "admin": ["@Maksimon777"],
    "katyasimonova": ["@maximoffn"]
}

# ======== ФАЙЛ С ДЕДЛАЙНАМИ =========
TASKS_FILE = 'deadlines.json'
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as f:
        json.dump([], f)

# ======== ФУНКЦИИ =========

async def mention_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().lstrip('@')
    users = target_users.get(text)
    if not users:
        await update.message.reply_text(f"Категория '{text}' не найдена.")
        return
    mentions = ' '.join(users)
    await update.message.reply_text(f"Внимание {text}! {mentions}")

async def add_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split('|')
        task_text = parts[0].replace('/дедлайн', '').strip()
        date_str = parts[1].strip()
        responsible = parts[2].strip()
        datetime.strptime(date_str, '%Y-%m-%d')  # проверка формата даты

        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)

        tasks.append({
            'task': task_text,
            'deadline': date_str,
            'responsible': responsible,
            'chat_id': update.message.chat_id
        })

        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)

        await update.message.reply_text(f"✅ Добавлено:\n📌 {task_text}\n📅 До: {date_str}\n👤 Ответственный: {responsible}")
    except Exception:
        await update.message.reply_text("❗️ Формат:\n`/дедлайн Текст задачи | ГГГГ-ММ-ДД | @username`", parse_mode='Markdown')

async def list_deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)
    if not tasks:
        await update.message.reply_text("📭 Пока нет активных дедлайнов.")
        return
    msg = "📋 Текущие дедлайны:\n"
    for i, task in enumerate(tasks, 1):
        msg += f"\n{i}. 📌 {task['task']} — 🗓 {task['deadline']} — 👤 {task['responsible']}"
    await update.message.reply_text(msg)

async def delete_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        n = int(update.message.text.split()[1])
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
        if 1 <= n <= len(tasks):
            deleted = tasks.pop(n - 1)
            with open(TASKS_FILE, 'w') as f:
                json.dump(tasks, f, indent=2)
            await update.message.reply_text(f"🗑 Удалено: {deleted['task']}")
        else:
            await update.message.reply_text("❌ Неверный номер задачи.")
    except Exception:
        await update.message.reply_text("⚠️ Используй: /удалить Номер", parse_mode='Markdown')

async def edit_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.replace('/редактировать', '', 1).strip().split('|')
        index = int(parts[0].strip()) - 1
        task_text = parts[1].strip()
        date_str = parts[2].strip()
        responsible = parts[3].strip()
        datetime.strptime(date_str, '%Y-%m-%d')

        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)

        tasks[index] = {
            'task': task_text,
            'deadline': date_str,
            'responsible': responsible,
            'chat_id': update.message.chat_id
        }

        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)

        await update.message.reply_text(f"✏️ Обновлено:\n📌 {task_text}\n📅 До: {date_str}\n👤 {responsible}")
    except Exception:
        await update.message.reply_text("⚠️ Используй:\n`/редактировать Номер | Новый текст | ГГГГ-ММ-ДД | @username`", parse_mode='Markdown')

async def check_deadlines(app: Application):
    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)
    now = datetime.now()
    for task in tasks:
        deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
        days_left = (deadline - now).days
        if days_left in [7, 3, 1]:
            try:
                await app.bot.send_message(
                    chat_id=task['chat_id'],
                    text=f"⏰ Напоминание!\n{task['responsible']}, дедлайн по задаче: \"{task['task']}\" — до {task['deadline']}"
                )
            except Exception as e:
                print(f"Ошибка отправки: {e}")

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = [
        "/дедлайн Текст задачи | ГГГГ-ММ-ДД | @username — добавить дедлайн",
        "/deadlines — показать все дедлайны",
        "/удалить Номер — удалить дедлайн",
        "/редактировать Номер | Новый текст | ГГГГ-ММ-ДД | @username — редактировать дедлайн",
        "/help — показать это сообщение",
        "Упоминание групп: просто напиши @all, @photo и т.п."
    ]
    await update.message.reply_text("Доступные команды:\n" + "\n".join(commands_list))

async def set_bot_commands(app: Application):
    commands = [
        BotCommand("deadline", "Добавить дедлайн"),
        BotCommand("deadlines", "Показать все дедлайны"),
        BotCommand("delete", "Удалить дедлайн по номеру"),
        BotCommand("edit", "Редактировать дедлайн"),
        BotCommand("help", "Список команд"),
    ]
    await app.bot.set_my_commands(commands)

# ======== ЗАПУСК БОТА =========
def main():
    BOT_TOKEN = "8265575566:AAEpgUGCGkzwaq99JGIaWko4g6y4mGW8ACA"
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики
    categories = list(target_users.keys())
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^@(' + '|'.join(categories) + r')\b'), mention_category))

    app.add_handler(CommandHandler("deadline", add_deadline))
    app.add_handler(CommandHandler("deadlines", list_deadlines))
    app.add_handler(CommandHandler("delete", delete_deadline))
    app.add_handler(CommandHandler("edit", edit_deadline))
    app.add_handler(CommandHandler("help", show_help))

    # Установка команд бота (синхронно перед запуском polling)
    import asyncio
    asyncio.get_event_loop().run_until_complete(set_bot_commands(app))

    # Планировщик напоминаний
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.create_task(check_deadlines(app)), 'interval', hours=24)
    scheduler.start()

    print("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
