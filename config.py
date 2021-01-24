import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

SQLITE_PATH = os.path.join(basedir, 'data.sqlite')


class BaseClass:
    SECRET_KEY = 'Umalat'
    CHEESE_PER_PAGE = 10
    CHEESE_MAKER_PER_PAGE = 10
    SKU_PER_PAGE = 100

    UPLOAD_TMP_FOLDER = 'app/data/tmp'
    STATS_FOLDER = 'app/data/stats'
    BOILING_PLAN_FOLDER = 'app/data/boiling_plan'
    SKU_PLAN_FOLDER = 'app/data/sku_plan'
    SCHEDULE_PLAN_FOLDER = 'app/data/schedule_plan'
    TEMPLATE_BOILING_PLAN = 'app/data/templates/constructor.xlsx'
    IGNORE_SKU_FILE = 'app/data/ignore/ignore_sku.json'
    with open(os.path.join(basedir, IGNORE_SKU_FILE), encoding='utf-8') as json_file:
        IGNORE_SKUS = json.load(json_file)

    SHEET_NAMES = {
        'remainings': 'файл остатки',
        'schedule_plan': 'планирование суточное',
        'water': 'Вода',
        'salt': 'Соль'
    }
    COLOURS = {
        'Для пиццы': '#E5B7B6',
        'Моцарелла': '#DAE5F1',
        'Фиор Ди Латте': '#CBC0D9',
        'Чильеджина': '#E5DFEC',
        'Качокавалло': '#F1DADA',
        'Сулугуни': '#F1DADA',
        'Терка': '#FFEBE0',
        'Default': '#FFFFFF',
        'DefaultGray': '#D9DDDC',
        'Remainings': '#F3F3C0'
    }
    ORDER = ['Фиор Ди Латте', 'Чильеджина', 'Моцарелла', 'Сулугуни', 'Для пиццы', 'Качокавалло', 'Терка']
    BOILING_VOLUME_LIMITS = {
        'MIN': 6000,
        'MAX': 8000
    }
    CONSTRUCTOR_CELLS = {
        'value': 'J',
        'remains_cumsum': 'K',
        'delimiter': 'L',
        'zeros': 'M',
        'start_row': 2
    }
    # cache files for 30 seconds
    CACHE_FILE_MAX_AGE = 30


class DebugConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = (os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + SQLITE_PATH) + '?check_same_thread=False'


class ProductionConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = (os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + SQLITE_PATH) + '?check_same_thread=False'


config = {
    'default': DebugConfig,
    'production': ProductionConfig,
    'debug': DebugConfig
}