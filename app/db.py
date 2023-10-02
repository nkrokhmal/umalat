from loguru import logger
from utils_ak.dict.dotdict import dotdict

from config import SQLITE_PATH


def create_external_db(data_path=None):

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    connection_string = create_connection_string(data_path)
    logger.info(f"Creating database session outside of the app {connection_string}.")
    engine = create_engine(connection_string)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    db = dotdict()
    db["session"] = session
    return db


def create_connection_string(db_path):
    db_path = db_path if db_path else SQLITE_PATH
    return f"sqlite:///{db_path}?check_same_thread=False"
