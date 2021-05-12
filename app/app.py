from app.imports.runtime import *

import app.models as umalat_models

from .main import main as main_bp


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

    app.register_blueprint(main_bp)
    return app


def create_manager(app):
    manager = flask_script.Manager(app)
    flask_migrate.Migrate(app, db, render_as_batch=True)
    manager.add_command("db", flask_migrate.MigrateCommand)

    admin = Admin(app, name="Umalat admin", template_mode="bootstrap3")
    for name, obj in inspect.getmembers(umalat_models):
        if inspect.isclass(obj) and isinstance(obj, mdb.Model):
            admin.add_view(ModelView(obj, db.session))
    return manager
