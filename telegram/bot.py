# -- IMPORTS --
import requests
from pathlib import Path
import os
from uuid import uuid4
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)

from templates import not_found_answer, error_answer

# -- ENV --
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_API_URL = os.environ["BOT_API_URL"]
BOT_API_KEY = os.environ["BOT_API_KEY"]
CLOUDFLARE_TEMP_URL = os.environ["TEMP_URL"]

# -- COMMANDS --
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Start msg")


# -- INLINE --
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    response = requests.post(
        BOT_API_URL + "sounds/",
        json={"telegram_id": user_id},
        headers={"Authorization": f"Bot {BOT_API_KEY}"},
    )

    if response.status_code == 200:
        sounds = response.json()
        answer = InlineQueryResultArticle(
            id=str(uuid4()),
            title=CLOUDFLARE_TEMP_URL,
            input_message_content=InputTextMessageContent(str(sounds)),
        )
    elif response.status_code == 404:
        answer = not_found_answer()

    else:
        answer = error_answer()

    await update.inline_query.answer([answer], cache_time=5)


# -- APPLICATION --
def main() -> None:
    application = Application.builder().token(os.environ.get("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
