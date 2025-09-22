import requests
import os
from uuid import uuid4
import logging
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)


BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_LIST_URL = os.environ["BOT_LIST_URL"]
BOT_API_KEY = os.environ["BOT_API_KEY"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Start msg")


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    response = requests.post(
        BOT_LIST_URL,
        json={"telegram_id": user_id},
        headers={"Authorization": f"Bot {BOT_API_KEY}"},
    )

    logging.info(response.json)

    if response.status_code == 200:
        sounds = response.json()
        answer = InlineQueryResultArticle(
            id=str(uuid4()),
            title="test",
            input_message_content=InputTextMessageContent(str(sounds)),
        )
    elif response.status_code == 404:
        keyboard_button = InlineKeyboardButton(
            text="🎵 Add sounds",
            url="http://127.0.0.1:8000/api/sounds/download",
        )

        reply_markup = InlineKeyboardMarkup([[keyboard_button]])

        answer = InlineQueryResultArticle(
            id="no_results_prompt",
            title="No sounds found...",
            description="Click here to open the web panel and add new sounds!",
            reply_markup=reply_markup,
            input_message_content=InputTextMessageContent(
                "Manage your sounds on th website"
            ),
        )
    else:
        answer = InlineQueryResultArticle(
            id="error_prompt",
            title="Oops! Error fetching sounds.",
            input_message_content=InputTextMessageContent("Test"),
        )

    await update.inline_query.answer([answer], cache_time=5)


def main() -> None:
    application = Application.builder().token(os.environ.get("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
