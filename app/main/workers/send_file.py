from app.imports.runtime import *
import telebot
from loguru import logger


DEPARTMENT_CHAT_ID = {
    "Моцарелла": flask.current_app.config["TELEGRAM_CHAT_MOZZARELLA_ID"],
    "Рикотта": flask.current_app.config["TELEGRAM_CHAT_RICOTTA_ID"],
    "Маскарпоне": flask.current_app.config["TELEGRAM_CHAT_MASCARPONE_ID"],
    "Масло": flask.current_app.config["TELEGRAM_CHAT_BUTTER_ID"],
    "Милкпроджект": flask.current_app.config["TELEGRAM_CHAT_MILKPROJECT_ID"],
}


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
    try:
        document = open(path, 'rb')
        tb.send_message(
            DEPARTMENT_CHAT_ID[department],
            f"Дата: {date} \nЦех: {department}  " + b"\xE2\x9C\x85".decode('utf-8')
        )
        tb.send_document(
            DEPARTMENT_CHAT_ID[department],
            document
        )
    except:
        pass


