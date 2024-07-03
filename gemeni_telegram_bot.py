import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from gemeni_python_format import get_response

load_dotenv('.env')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY_GOOGLE')

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = get_response(user_message)
    await update.message.reply_text(response)

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
