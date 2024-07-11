import logging
import os
import re
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from llama3_python_format import get_response
from telegram.constants import ChatAction

load_dotenv('.env')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY_LLAMA')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_latex(text: str) -> str:
    """
    Эта функция заменяет специальные символы в строке на их экранированные версии.

    Args:
        text (str): входная строка.

    Returns:
        str: выходная строка с замененными символами.
    """
    escape_chars = ['\\', '.', '-', '=', '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '!', '{', '}', '$']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def convert_latex_to_human_readable(latex: str) -> str:
    """
    Эта функция преобразует строку в формате LaTeX в более понятный для человека формат.

    Args:
        latex (str): входная строка в формате LaTeX.

    Returns:
        str: выходная строка в более понятном для человека формате.
    """
    # Замена обозначений дробных частей
    human_readable = latex.replace(r'\frac{', '(').replace(r'}{', ') / (').replace(r'}', ')')
    # Замена умножения на перекрестное произведение
    human_readable = human_readable.replace(r'\cdot', '⋅')
    # Удаление выравнивания
    human_readable = human_readable.replace(r'\left', '').replace(r'\right', '')
    # Удаление обозначений вроде $$...$$
    human_readable = human_readable.replace('$$', '').replace('$', '')
    # Замена двойных круглых скобок внутри двойных круглых скобок на простые
    human_readable = re.sub(r'\(\(([^()]+)\)\)', r'(\1)', human_readable)
    # Замена простых круглых скобок, содержащих только буквы или цифры, на сами буквы или цифры
    human_readable = re.sub(r'\(([A-Za-z0-9_]+)\)', r'\1', human_readable)
    # Замена круглых скобок, содержащих деление, на деление
    human_readable = re.sub(r'\(([^()]+) / ([^()]+)\)', r'(\1 / \2)', human_readable)
    # Замена степенной записи с градусом на символ градуса 
    human_readable = re.sub(r'(\d+)\^{\s*\\circ\s*}', r'\1°', human_readable)

    
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