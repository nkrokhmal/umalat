from app.imports.external import *
from app.db import create_external_db

model_db = mdb = flask_sqlalchemy.SQLAlchemy()

if os.environ.get("ENVIRONMENT") == "runtime":
    db = mdb
else:
    db = create_external_db()

bootstrap = flask_bootstrap.Bootstrap()
page_down = flask_pagedown.PageDown()
