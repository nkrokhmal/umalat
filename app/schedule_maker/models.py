from app.models_new import *

from utils_ak.interactive_imports import *
from config import SQLITE_PATH


def get_db(environment=None):
    environment = environment or os.getenv('environment')

    if environment == 'flask_app':
        from app import db
    elif environment == 'interactive':
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(f"sqlite:///{SQLITE_PATH}")
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        db = dotdict()
        db['session'] = session
    else:
        raise Exception(f'Enviroment {environment} not supported')
    return db

db = None
def set_global_db(environment=None):
    global db
    db = get_db(environment)

set_global_db()


def query_exactly_one(cls, key, value):
    query = db.session.query(cls).filter(getattr(cls, key) == value)
    res = query.all()

    if len(res) == 0:
        raise Exception('Failed to fetch element {} {} {}'.format(cls, key, value))
    elif len(res) > 1:
        raise Exception('Fetched too many elements {} {} {}: {}'.format(cls, key, value, res))
    else:
        return res[0]


def cast_sku(obj):
    if isinstance(obj, SKU):
        return obj
    elif is_int_like(obj):
        return query_exactly_one(SKU, 'id', int(float(obj)))
    elif isinstance(obj, str):
        return query_exactly_one(SKU, 'name', obj)
    else:
        raise Exception('Unknown sku type')


def cast_packer(obj):
    if isinstance(obj, Packer):
        return obj
    elif is_int_like(obj):
        return query_exactly_one(Packer, 'id', int(float(obj)))
    elif isinstance(obj, str):
        return query_exactly_one(Packer, 'name', obj)
    elif isinstance(obj, SKU):
        return cast_packer(obj.packer_id)
    else:
        raise Exception('Unknown packer type')


def cast_boiling(obj):
    if isinstance(obj, Boiling):
        return obj
    elif is_int_like(obj):
        return query_exactly_one(Boiling, 'id', int(float(obj)))
    elif isinstance(obj, str):
        try:
            # water, 2.7, Альче
            values = obj.split(',')
            boiling_type, percent, ferment = values[:3]
            percent = percent.replace(' ', '')
            ferment = re.sub(spaces_on_edge('beg'), '', ferment)
            ferment = re.sub(spaces_on_edge('end'), '', ferment)
            is_lactose = len(values) < 4
            query = db.session.query(Boiling).filter((Boiling.percent == percent) & (Boiling.is_lactose == is_lactose) & (Boiling.ferment == ferment))
            boilings = query.all()
            boilings = [b for b in boilings if b.boiling_type == boiling_type]
            # todo: uncom
            # assert len(boilings) == 1
            return boilings[0]
        except:
            raise Exception('Unknown boiling')
    else:
        raise Exception(f'Unknown boiling')


def cast_boiling_form_factor(obj):
    if isinstance(obj, BoilingFormFactor):
        return obj
    elif is_int_like(obj):
        return query_exactly_one(BoilingFormFactor, 'id', int(float(obj)))
    else:
        raise Exception(f'Unknown boiling form factor {type(obj)}')

