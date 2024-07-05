import logging
import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from gemeni_python_format import get_response
from telegram.constants import ChatAction

load_dotenv('.env')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY_GOOGLE')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_latex(text: str) -> str:
    escape_chars = ['\\', '.', '-', '=', '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '!', '{', '}', '$']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def convert_latex_to_human_readable(latex: str) -> str:
    human_readable = latex.replace(r'\frac{', '(').replace(r'}{', ') / (').replace(r'}', ')')
    human_readable = human_readable.replace(r'\cdot', '⋅')
    human_readable = human_readable.replace(r'\left', '').replace(r'\right', '')
    human_readable = human_readable.replace('$$', '').replace('$', '')
    return human_readable

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        user_message = update.message.text
        response = get_response(user_message)

        human_readable_response = convert_latex_to_human_readable(response)
        escaped_response = escape_latex(human_readable_response)

        await update.message.reply_markdown_v2(f"{escaped_response}")

    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        await update.message.reply_text("Извините, произошла ошибка при обработке вашего запроса.")

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()