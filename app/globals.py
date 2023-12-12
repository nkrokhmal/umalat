import flask_login
import utils_ak.loguru

from utils_ak.lazy_tester.lazy_tester_class import lazy_tester
from utils_ak.loguru.configuration import format_with_trace

from app.db import create_external_db
from app.imports.external import *

# from app.notifier import Notifier
from config import config


model_db = mdb = flask_sqlalchemy.SQLAlchemy()

if os.environ.get("APP_ENVIRONMENT") == "runtime":
    db = mdb
else:
    db = create_external_db()

bootstrap = flask_bootstrap.Bootstrap()
page_down = flask_pagedown.PageDown()
rq = flask_rq2.RQ()
login_manager = flask_login.LoginManager()

ERROR = 1e-5

basedir = os.path.dirname(os.path.dirname(__file__))

lazy_tester.configure(root=os.path.join(basedir, "tests/lazy_tester_logs"), app_path=basedir)

# notifier = Notifier()

# configure loguru for telegram notifications
# logger.add(
#     NotificationHandler("telegram", defaults={"token": config.TELEGRAM_BOT_TOKEN, "chat_id": config.TELEGRAM_CHAT_ID}),
#     level="WARNING",
#     format=format_with_trace,
# )
