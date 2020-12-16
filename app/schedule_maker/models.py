from app.models import *

from utils_ak.interactive_imports import *

if os.getenv('mode') == 'prod':
    from app import db
elif os.getenv('mode') == 'dev':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    sqlite_filepath = r"C:\Users\Mi\Desktop\code\git\2020.10-umalat\umalat\data.sqlite"
    engine = create_engine(f"sqlite:///{sqlite_filepath}")
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    db = dotdict()
    db['session'] = session


def cast_sku(obj):
    if isinstance(obj, SKU):
        return obj
    elif isinstance(obj, (str, int)):
        # try to return by id if int-like
        try:
            obj = str(int(obj))
            return db.session.query(SKU).filter(SKU.id == obj).first()
        except:
            pass

        # return by name
        return db.session.query(SKU).filter(SKU.name == str(obj)).first()
    else:
        raise Exception('Unknown sku type')


def cast_packer(obj):
    if isinstance(obj, Packer):
        return obj
    elif isinstance(obj, int):
        return db.session.query(Packer).filter(Packer.id == obj).first()
    if isinstance(obj, SKU):
        return cast_packer(obj.packer_id)
    else:
        raise Exception('Unknown packer type')


def cast_boiling(obj):
    if isinstance(obj, Boiling):
        return obj
    elif isinstance(obj, (str, int)):
        obj = str(obj)
        return db.session.query(Boiling).filter(Boiling.id == obj).first()
    else:
        raise Exception(f'Unknown boiling type {type(obj)}')

