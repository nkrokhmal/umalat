from app.models_new import *

from app.enum import LineName

from utils_ak.interactive_imports import *
from config import SQLITE_PATH


def get_db(environment=None):
    environment = environment or os.getenv('environment')

    if environment == 'flask_app':
        from app import db
    elif environment == 'interactive':
        print('WORKING IN INTERACTIVE MODE')
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


def cast_model(cls, obj, int_attribute='id', str_attribute='name'):
    if isinstance(obj, cls):
        return obj
    elif is_int_like(obj):
        return query_exactly_one(cls, int_attribute, int(float(obj)))
    elif isinstance(obj, str):
        return query_exactly_one(cls, str_attribute, obj)
    else:
        raise Exception(f'Unknown {cls} type')


def cast_sku(obj):
    return cast_model(SKU, obj)


def cast_line(obj):
    return cast_model(Line, obj)


def cast_packer(obj):
    return cast_model(Packer, obj)


def cast_pack_type(obj):
    return cast_model(PackType, obj)


def cast_boiling_technology(obj):
    return cast_model(BoilingTechnology, obj)


def get_termizator():
    return db.session.query(Termizator).first()


def cast_group(obj):
    return cast_model(Group, obj)


def cast_form_factor(obj):
    return cast_model(FormFactor, obj)


def cast_boiling(obj):
    if isinstance(obj, str):
        try:
            # water, 2.7, Альче
            values = obj.split(',')
            line_name, percent, ferment = values[:3]
            percent = percent.replace(' ', '')
            ferment = re.sub(spaces_on_edge('beg'), '', ferment)
            ferment = re.sub(spaces_on_edge('end'), '', ferment)
            is_lactose = len(values) < 4
            query = db.session.query(Boiling).filter((Boiling.percent == percent) & (Boiling.is_lactose == is_lactose) & (Boiling.ferment == ferment))
            boilings = query.all()
            boilings = [b for b in boilings if b.line.name == line_name]
        except:
            raise Exception('Unknown boiling')

        if len(boilings) == 0:
            raise Exception(f'Boiling {obj} not found')
        elif len(boilings) > 1:
            raise Exception(f'Found multiple boilings {obj}')

        return boilings[0]

    return cast_model(Boiling, obj)
