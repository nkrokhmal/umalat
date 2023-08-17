from app.imports.runtime import *

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import app.models as umalat_models

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


def create_manager(app: flask.Flask) -> None:
    db_folder: str = 'test' if app.config["TESTING"] else 'prod'
    migration_dir: str = os.path.join('db', db_folder, 'migrations')

    flask_migrate.Migrate(app, db, render_as_batch=True, directory=migration_dir)
    # app.cli.add_command(migrate)

    admin = Admin(app, name="Umalat admin", template_mode="bootstrap3")
    for name, obj in inspect.getmembers(umalat_models):
        if inspect.isclass(obj) and issubclass(obj, mdb.Model):
            admin.add_view(ModelView(obj, db.session))
