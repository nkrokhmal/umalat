from app.imports.external import *

from config import SQLITE_PATH


def create_external_db(data_path=None):
    logger.info("Creating database session outside of the app.")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    connection_string = f"sqlite:///{data_path or SQLITE_PATH}?check_same_thread=False"
    engine = create_engine(connection_string)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    db = utils.dotdict()
    db["session"] = session
    return db
