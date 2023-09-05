from utils_ak.time import cast_datetime, cast_str

from app.imports.external import *
from config import config


class Notifier:
    @staticmethod
    def _urgency_symbol(level):
        if level == 0:
            return "⚪"
        elif level == 1:
            return "🔵"
        elif level == 2:
            return "🟡"
        else:
            return "🔴" * min(level - 2, 10)

    @staticmethod
    def notify(topic, message, urgency=0):
        tb = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        date_str = cast_str(
            cast_datetime(datetime.now()), "%Y-%m-%d %H:%M:%S"
        )  # date without microseconds, 2022-02-04 15:29:44
        tb.send_message(
            config.TELEGRAM_CHAT_ID, "\n".join([date_str, Notifier._urgency_symbol(urgency), topic, message])
        )
