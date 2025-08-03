from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

target_users = {
    "all": [
        "@miiglluna", #Милена
        "@Ikc0ta",
        "@derlegen",
        "@Friderico_dourden",
        "@maximoffn",
        "@r_shrlv",
        "@FLYINGeyesOFFICIAL21",
        "@astor602",
        "@Maksimon777",
        "@alexa_vasyaeva"
    ],
    "photo": [
        "@miiglluna",
        "@derlegen",
        "@FLYINGeyesOFFICIAL21"
    ],
    "designer": [
        "@Ikc0ta",
        "@maximoffn"
    ],
    "copy": [
        "@alexa_vasyaeva",
        "@astor602"
    ],
    "video": [
        "@Friderico_dourden",
        "@r_shrlv"
    ],
    "admin": [
        "@Maksimon777"
    ],
    "КатяСимонова": [
        "@maximoffn"
    ]
}


async def mention_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    command = text.lstrip('@')  # убираем @

    users = target_users.get(command)
    if not users:
        await update.message.reply_text(f"Категория '{command}' не найдена.")
        return

    mentions = ' '.join(users)
    await update.message.reply_text(f"Внимание {command}! {mentions}")


def main():
    BOT_TOKEN = "8265575566:AAHi2fIhmyBlFnL_NYHkQm8-26EAhFO-HFY"
    app = Application.builder().token(BOT_TOKEN).build()

    # Отслеживаем сообщения, которые начинаются с нужных команд
    commands = ['@all', '@video', '@photo', '@designer', '@copy', '@admin', '@КатяСимонова']

    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r'^@(' + '|'.join(cmd.lstrip('@') for cmd in commands) + r')\b'),
                       mention_category))

    app.run_polling()


if __name__ == '__main__':
    main()
