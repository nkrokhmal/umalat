from app.imports.runtime import *
import telebot


@rq.job
def send_file(path):
    tb = telebot.TeleBot(
        flask.current_app.config["TELEGRAM_BOT_TOKEN"]
    )
    document = open(path, 'rb')
    tb.send_message(
        flask.current_app.config["TELEGRAM_CHAT_FILES_ID"],
        "Подтверждено расписание"
    )
    tb.send_document(
        flask.current_app.config["TELEGRAM_CHAT_FILES_ID"],
        document
    )


