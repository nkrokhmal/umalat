from app.imports.runtime import *
import telebot
from loguru import logger


@rq.job
def send_file(path, date, department):
    tb = telebot.TeleBot(
        flask.current_app.config["TELEGRAM_BOT_TOKEN"]
    )
    document = open(path, 'rb')
    tb.send_message(
        flask.current_app.config["TELEGRAM_CHAT_FILES_ID"],
        f"Дата: {date} \nЦех: {department}  " + b"\xE2\x9C\x85".decode('utf-8')
    )
    tb.send_document(
        flask.current_app.config["TELEGRAM_CHAT_FILES_ID"],
        document
    )


