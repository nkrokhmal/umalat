from app.imports.external import *
from typing import Optional

basedir = os.path.abspath(os.path.dirname(__file__))

SQLITE_PATH = os.path.join(basedir, "db/prod/data.sqlite")
TEST_SQLITE_PATH = os.path.join(basedir, "db/test/data.sqlite")


class BaseClass:
    PROPAGATE_EXCEPTIONS = False
    SECRET_KEY = "Umalat"
    CHEESE_PER_PAGE = 10
    CHEESE_MAKER_PER_PAGE = 10
    SKU_PER_PAGE = 10

    DATE_FORMAT = "%Y-%m-%d"

    BATCH_NUMBERS_DIR = "db/batch_numbers"

    DYNAMIC_DIR = "app/data/dynamic"
    BATCH_NUMBER_DIR = "db/batch_numbers/"

    UPLOAD_TMP_FOLDER = "app/data/dynamic/tmp"
    STATS_FOLDER = "app/data/dynamic/stats"
    BOILING_PLAN_FOLDER = "app/data/dynamic/boiling_plan"
    SKU_PLAN_FOLDER = "app/data/dynamic/sku_plan"
    SCHEDULE_PLAN_FOLDER = "app/data/dynamic/schedule_plan"
    TOTAL_SCHEDULE_TASK_FOLDER = "app/data/dynamic/schedule_task"

    TEMPLATE_MOZZARELLA_BOILING_PLAN = (
        "app/data/static/templates/constructor_mozzarella.xlsx"
    )
    TEMPLATE_RICOTTA_BOILING_PLAN = "app/data/static/templates/constructor_ricotta.xlsx"
    TEMPLATE_MASCARPONE_BOILING_PLAN = (
        "app/data/static/templates/constructor_mascarpone.xlsx"
    )
    TEMPLATE_BUTTER_BOILING_PLAN = (
        "app/data/static/templates/constructor_butter.xlsx"
    )
    TEMPLATE_MILKPROJECT_BOILING_PLAN = (
        "app/data/static/templates/constructor_milkproject.xlsx"
    )
    TEMPLATE_SCHEDULE_PLAN = "app/data/static/templates/constructor_schedule.xlsx"

    IGNORE_SKU_FILE = "app/data/static/ignore/ignore_sku.json"
    with open(os.path.join(basedir, IGNORE_SKU_FILE), encoding="utf-8") as json_file:
        IGNORE_SKUS = json.load(json_file)

    SHEET_NAMES = {
        "remainings": "файл остатки",
        "schedule_plan": "планирование суточное",
        "water": "Вода",
        "salt": "Соль",
    }
    COLORS = {
        "Для пиццы": "#E5B7B6",
        "Моцарелла": "#DAE5F1",
        "Фиор Ди Латте": "#CBC0D9",
        "Чильеджина": "#E5DFEC",
        "Качокавалло": "#F1DADA",
        "Сулугуни": "#F1DADA",
        "Терка": "#FFEBE0",
        "Default": "#FFFFFF",
        "DefaultGray": "#D9DDDC",
        "Remainings": "#F3F3C0",
        "Рикотта": "#A3D5D2",
        "Маскарпоне": "#E5B7B6",
        "Кремчиз": "#DAE5F1",
        "Творожный": "#CBC0D9",
        "Робиола": "E5DFEC",
        "Сливки": "#F1DADA",
    }
    ORDER = [
        "Фиор Ди Латте",
        "Чильеджина",
        "Моцарелла",
        "Сулугуни",
        "Для пиццы",
        "Качокавалло",
        "Терка",
        "Рикотта",
        "Маскарпоне",
        "Кремчиз",
        "Творожный",
        "Робиола",
        "Сливки",
    ]
    BOILING_VOLUME_LIMITS = {"MIN": 6000, "MAX": 8000}
    CONSTRUCTOR_CELLS = {
        "value": "J",
        "remains_cumsum": "K",
        "delimiter": "L",
        "zeros": "M",
        "start_row": 2,
    }
    # cache files for 30 seconds
    CACHE_FILE_MAX_AGE = 30

    DEFAULT_RUBBER_FORM_FACTOR = "Соль: 460"

    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[int] = None

    @staticmethod
    def abs_path(local_path):
        return os.path.join(basedir, local_path)


class DebugConfig(BaseClass):
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + SQLITE_PATH
    ) + "?check_same_thread=False"


class ProductionConfig(BaseClass):
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + SQLITE_PATH
    ) + "?check_same_thread=False"


class TestConfig(BaseClass):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + TEST_SQLITE_PATH
    ) + "?check_same_thread=False"
    TEST_MOZZARELLA = "app/data/tests/mozzarella_plan.xlsx"
    TEST_RICOTTA = "app/data/tests/ricotta_plan.xlsx"
    TEST_MASCARPONE = "app/data/tests/mascarpone_plan.xlsx"
    TEST_MILKPROJECT = "app/data/tests/milkproject_plan.xlsx"
    TEST_BUTTER = "app/data/tests/butter_plan.xlsx"

    TELEGRAM_BOT_TOKEN = "1101281504:AAEbWzUXem-FK7Yb2RHvkg-h8sMilZAuFpA"
    TELEGRAM_CHAT_ID = -544068496


configs = {
    "default": DebugConfig,
    "production": ProductionConfig,
    "debug": DebugConfig,
    "test": TestConfig,
}
