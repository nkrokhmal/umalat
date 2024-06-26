import os


os.environ["APP_ENVIRONMENT"] = "runtime"
os.environ["DB_TYPE"] = "prod"

from app.app import *


app, rq = create_app()
create_manager(app)

if __name__ == "__main__":
    from app.models.fill_db.default_data import generate_all
    from app.models.fill_db.fill_adygea import fill_db as adygea_fill_db
    from app.models.fill_db.fill_brynza import BrynzaFiller
    from app.models.fill_db.fill_butter import fill_db as butter_fill_db
    from app.models.fill_db.fill_mascarpone import fill_db as mascarpone_fill_db
    from app.models.fill_db.fill_milk_project import fill_db as milk_project_fill_db
    from app.models.fill_db.fill_mozzarella import fill_db as mozzarella_fill_db
    from app.models.fill_db.fill_ricotta import RicottaFiller
    from app.models.fill_db.fill_halumi import HalumiFiller

    with app.app_context():
        generate_all()
        BrynzaFiller().fill_db()
        RicottaFiller().fill_db()
        adygea_fill_db()
        milk_project_fill_db()
        butter_fill_db()
        mozzarella_fill_db()
        mascarpone_fill_db()
        HalumiFiller().fill_db()
