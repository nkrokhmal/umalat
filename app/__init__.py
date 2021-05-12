from flask import Flask

from utils_ak.os import makedirs

from config import configs

from .main import main as main_bp
from .globals import db, bootstrap, page_down


def create_app(config_name="default"):
    config = configs[config_name]

    # init directories
    for local_path in [
        config.UPLOAD_TMP_FOLDER,
        config.STATS_FOLDER,
        config.BOILING_PLAN_FOLDER,
        config.SKU_PLAN_FOLDER,
        config.SCHEDULE_PLAN_FOLDER,
    ]:
        makedirs(config.abs_path(local_path) + "/")

    # init directories for files
    for local_path in [
        config.TEMPLATE_MOZZARELLA_BOILING_PLAN,
        config.TEMPLATE_RICOTTA_BOILING_PLAN,
        config.TEMPLATE_MASCARPONE_BOILING_PLAN,
        config.IGNORE_SKU_FILE,
    ]:
        makedirs(config.abs_path(local_path))

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    bootstrap.init_app(app)
    page_down.init_app(app)

    app.register_blueprint(main_bp)

    return app
