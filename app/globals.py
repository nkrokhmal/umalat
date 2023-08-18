import flask_login
import utils_ak.loguru

from app.create_external_db import create_external_db
from app.imports.external import *

from config import config


# - DB

model_db = mdb = flask_sqlalchemy.SQLAlchemy()

if os.environ.get("APP_ENVIRONMENT") == "runtime":
    db = mdb
else:
    db = create_external_db()

# - Flask globals

bootstrap = flask_bootstrap.Bootstrap()
page_down = flask_pagedown.PageDown()
rq = flask_rq2.RQ()
login_manager = flask_login.LoginManager()

# - Error constant

ERROR = 1e-5

# - Configure loguru # todo later: move to runtime [@marklidenberg]

basedir = os.path.dirname(os.path.dirname(__file__))

utils.lazy_tester.configure(root=os.path.join(basedir, "tests/lazy_tester_logs"), app_path=basedir)

# configure loguru for telegram notifications
logger.add(
    NotificationHandler("telegram", defaults={"token": config.TELEGRAM_BOT_TOKEN, "chat_id": config.TELEGRAM_CHAT_ID}),
    level="WARNING",
    format=utils_ak.loguru.format_with_trace,
)
