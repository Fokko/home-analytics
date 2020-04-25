import logging
import os

from optimize import cancel_schema, make_charging_schema
from telegram import ParseMode
from telegram.ext import CommandHandler, Updater

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


def authorized(update, context) -> bool:
    if update.message.from_user.id != 14838371:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="*Not authorized*", parse_mode=ParseMode.MARKDOWN_V2
        )
        return False
    return True


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    help_message(update, context)


def help_message(update, context):
    """Send a message when the command /help is issued."""
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="""*Options:*
*/charge*: Will schedule a charge moment
*/cancel*: Will cancel all scheduled charging moments
        """,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def charge(update, context):
    """Log Errors caused by Updates."""
    if authorized(update, context):
        cancel_schema()
        schema = make_charging_schema()
        msg = f"""*Schema:*
```
{schema}
```
        """
        logger.info(msg)
        context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)


def cancel(update, context):
    if authorized(update, context):
        cancel_schema()
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="*Cancelled the charging schema*",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("charge", charge))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(CommandHandler("help", help_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
