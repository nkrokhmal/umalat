from app.imports.runtime import *
import telebot


@rq.job
def send_file(path, date, department):
    tb = telebot.TeleBot(
        flask.current_app.config["TELEGRAM_BOT_TOKEN"]
    )
    document = open(path, 'rb')
    tb.send_message(
        flask.current_app.config["TELEGRAM_CHAT_FILES_ID"],
        f"{date} \n {department} \n Подтверждено расписание"
    )
    tb.send_document(
        flask.current_app.config["TELEGRAM_CHAT_FILES_ID"],
        document
    )


