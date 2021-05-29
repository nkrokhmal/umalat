from app.imports.external import *

from config import SQLITE_PATH


def create_external_db(data_path=None):
    logger.info("Creating database session outside of the app.")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    connection_string = create_connection_string(data_path)
    engine = create_engine(connection_string)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    db = utils.dotdict()
    db["session"] = session
    return db


def create_connection_string(db_path):
    db_path = db_path if db_path else SQLITE_PATH
    return f"sqlite:///{db_path}?check_same_thread=False"
