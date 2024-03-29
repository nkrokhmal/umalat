import os


os.environ["APP_ENVIRONMENT"] = "runtime"
os.environ["DB_TYPE"] = "test"

from app.app import create_app, create_manager
from app.models.fill_db.default_data import generate_all
from app.models.fill_db.fill_adygea import fill_db as adygea_fill_db
from app.models.fill_db.fill_butter import fill_db as butter_fill_db
from app.models.fill_db.fill_mascarpone import fill_db as mascarpone_fill_db
from app.models.fill_db.fill_milk_project import fill_db as milk_project_fill_db
from app.models.fill_db.fill_mozzarella import fill_db as mozzarella_fill_db
from app.models.fill_db.fill_ricotta import RicottaFiller


app, _ = create_app("test")
create_manager(app)

if __name__ == "__main__":
    with app.app_context():
        generate_all()
        RicottaFiller.fill_db()
        adygea_fill_db()
        milk_project_fill_db()
        butter_fill_db()
        mozzarella_fill_db()
        mascarpone_fill_db()
