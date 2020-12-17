import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseClass:
    SECRET_KEY = 'Umalat'
    CHEESE_PER_PAGE = 10
    CHEESE_MAKER_PER_PAGE = 10
    SKU_PER_PAGE = 100
    UPLOAD_TMP_FOLDER = 'app/data/tmp'
    STATS_FOLDER = 'app/data/stats'
    STATS_LINK_FOLDER = 'data/stats'
    CONSTRUCTOR_FOLDER = 'app/data/constructor'
    CONSTRUCTOR_LINK_FOLDER = 'data/constructor'
    BOILING_PLAN_FOLDER = 'data/constructor'
    SKU_PLAN_FOLDER = 'data/plan'
    SCHEDULE_PLAN_FOLDER = '/data/schedule'
    CONSTRUCTOR_CELLS = {
        'value': 'J',
        'remains_cumsum': 'K',
        'delimiter': 'L',
        'zeros': 'M',
        'start_row': 2
    }

class DebugConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class ProductionConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'default': DebugConfig,
    'production': ProductionConfig,
    'debug': DebugConfig
}