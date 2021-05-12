from app.imports.external import *
from app.db import create_external_db

model_db = mdb = flask_sqlalchemy.SQLAlchemy()

if os.environ.get("environment") == "interactive":
    db = create_external_db()
else:
    db = mdb

bootstrap = flask_bootstrap.Bootstrap()
page_down = flask_pagedown.PageDown()
