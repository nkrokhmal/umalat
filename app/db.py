from app.imports.external import *

from config import SQLITE_PATH


def create_external_db():
    logger.info("Creating database session outside of the app.")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(f"sqlite:///{SQLITE_PATH}?check_same_thread=False")
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    db = utils.dotdict()
    db["session"] = session
    return db
