from app.imports.runtime import *

from .main import main as main_bp
from .main.errors import not_found


def create_app(config_name="default"):
    config = configs[config_name]

    # init directories
    for local_path in [
        config.BATCH_NUMBERS_DIR,
        config.UPLOAD_TMP_FOLDER,
        config.SKU_PLAN_FOLDER,
    ]:
        utils.makedirs(config.abs_path(local_path) + "/")

    # init directories for files
    for local_path in [
        config.TEMPLATE_MOZZARELLA_BOILING_PLAN,
        config.TEMPLATE_RICOTTA_BOILING_PLAN,
        config.TEMPLATE_MASCARPONE_BOILING_PLAN,
        config.IGNORE_SKU_FILE,
    ]:
        utils.makedirs(config.abs_path(local_path))

    app = flask.Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    bootstrap.init_app(app)
    page_down.init_app(app)
    login_manager.init_app(app)
    rq.init_app(app)

    app.register_blueprint(main_bp)
    app.register_error_handler(404, not_found)
    return app, rq
