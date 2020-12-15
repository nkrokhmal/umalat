import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseClass:
    SECRET_KEY = 'Umalat'
    CHEESE_PER_PAGE = 10
    CHEESE_MAKER_PER_PAGE = 10
    SKU_PER_PAGE = 100

class DebugConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class ProductionConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'default': DebugConfig,
    'production': ProductionConfig,
    'debug': DebugConfig
}