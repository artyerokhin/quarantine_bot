import logging

from helpers import generate_map, TELEGRAM_BOT_KEY
from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text(
        "Приет! Нажмите /zone и ваш адрес в текстовом виде, чтобы увидеть допустимую зону (100 метров) от вашего адреса"
    )


def zone(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        address = " ".join(context.args)
        if not address:
            context.bot.send_message(
                chat_id=chat_id,
                text="Адрес пуст, формат команды: /zone Адрес в виде текста (напр. Москва, Твардовского 21)",
            )
        elif generate_map(address, "images/{}.png".format(chat_id)):
            send_image(context, chat_id)
        else:
            context.bot.send_message(chat_id=chat_id, text="Что-то пошло не так :(")
    except Exception as e:
        print(e)
        update.message.reply_text(
            "Пример использования: /zone Адрес в виде текста (напр. Москва, Твардовского 21)>"
        )


def send_image(context, chat_id):
    """Send a message with image"""
    chat_id = chat_id
    context.bot.send_message(chat_id=chat_id, text="Допустимая зона готова!")
    context.bot.send_photo(
        chat_id=chat_id, photo=open("images/{}.png".format(chat_id), "rb")
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Run bot."""

    updater = Updater(TELEGRAM_BOT_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(
        CommandHandler(
            "zone", zone, pass_args=True, pass_job_queue=True, pass_chat_data=True
        )
    )

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
