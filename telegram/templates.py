# -- IMPORTS --
from uuid import uuid4
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultCachedVoice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


# -- TEMPLATES --
class InlineTemplate:
    _add_sounds_button = InlineKeyboardButton(
        text="🎵 Add sounds",
        url="https://telepad.cc",
    )

    NOT_FOUND = InlineQueryResultArticle(
        id="no_results_prompt",
        title="No sounds found...",
        description="Click here to open the web panel and add new sounds!",
        reply_markup=InlineKeyboardMarkup([[_add_sounds_button]]),
        input_message_content=InputTextMessageContent("Add your sounds on the website"),
    )

    ERROR = InlineQueryResultArticle(
        id="error_prompt",
        title="Oops! Error fetching sounds.",
        description="Try again later!",
        input_message_content=InputTextMessageContent("Sorry, something is broken..."),
    )

    def inline_sound(sound: dict) -> InlineQueryResultCachedVoice:
        return InlineQueryResultCachedVoice(
            id=str(uuid4()),
            voice_file_id=sound["file_id"],
            title=sound["name"],
        )


class MessageTemplate:
    START = (
        "💬 • Welcome!\n\n"
        "🔎 • Type <b>@tlpadbot</b> in any chat\n"
        "          to look for your sounds.\n\n"
        "🔉 • Manage your sounds on\n"
        "          <b>telepad.cc</b> or send any file or link\n"
        "          to this chat.\n\n"
        "💠 • Enjoy using <b>Telepad</b>!"
    )
