from flask import Flask
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import config

from .init import *

db = SQLAlchemy()
bootstrap = Bootstrap()
page_down = PageDown()


def create_app():
    app = Flask(__name__)
    config_name = "default"
    app.config.from_object(config[config_name])

    db.init_app(app)
    bootstrap.init_app(app)
    page_down.init_app(app)

    from .main import main as main_bp

    app.register_blueprint(main_bp)

    return app, db
