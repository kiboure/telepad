# -- IMPORTS --
import os
import requests
from telegram import Update, constants
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)

from templates import InlineTemplate, MessageTemplate

# -- ENV --
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_API_URL = os.environ["BOT_API_URL"]
BOT_API_KEY = os.environ["BOT_API_KEY"]


# -- COMMANDS --
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        MessageTemplate.START, parse_mode=constants.ParseMode.HTML
    )


# -- INLINE --
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    response = requests.post(
        BOT_API_URL + "sounds/",
        json={"telegram_id": user_id},
        headers={"Authorization": f"Bot {BOT_API_KEY}"},
    )
    if response.status_code != 200:
        await update.inline_query.answer([InlineTemplate.ERROR], cache_time=5)
        return

    sounds = response.json()
    if not sounds:
        answer = [InlineTemplate.NOT_FOUND]
    else:
        answer = [InlineTemplate.inline_sound(sound) for sound in sounds]

    await update.inline_query.answer(answer, cache_time=5)


# -- APPLICATION --
def main() -> None:
    application = Application.builder().token(os.environ.get("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
