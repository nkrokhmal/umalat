import inspect
import os

import flask_migrate
import flask_script

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import models as umalat_models
from app.globals import db, mdb


def create_manager(app):
    DB_FOLDER = "test" if app.config["TESTING"] else "prod"
    MIGRATION_DIR = os.path.join("db", DB_FOLDER, "migrations")

    manager = flask_script.Manager(app)
    flask_migrate.Migrate(app, db, render_as_batch=True, directory=MIGRATION_DIR)
    manager.add_command("db", flask_migrate.MigrateCommand)

    admin = Admin(app, name="Umalat admin", template_mode="bootstrap3")
    for name, obj in inspect.getmembers(umalat_models):
        if inspect.isclass(obj) and issubclass(obj, mdb.Model):
            admin.add_view(ModelView(obj, db.session))
    return manager
