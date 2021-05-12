from app.imports.external import *
from app.db import create_external_db

model_db = mdb = SQLAlchemy()

if os.environ.get("environment") == "interactive":
    db = create_external_db()
else:
    db = mdb

bootstrap = Bootstrap()
page_down = PageDown()
