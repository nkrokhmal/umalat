import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

SQLITE_PATH = os.path.join(basedir, "db/data.sqlite")


class BaseClass:
    PROPAGATE_EXCEPTIONS = False
    SECRET_KEY = "Umalat"
    CHEESE_PER_PAGE = 10
    CHEESE_MAKER_PER_PAGE = 10
    SKU_PER_PAGE = 10

    UPLOAD_TMP_FOLDER = "app/data/tmp"
    STATS_FOLDER = "app/data/stats"
    BOILING_PLAN_FOLDER = "app/data/boiling_plan"
    SKU_PLAN_FOLDER = "app/data/sku_plan"
    SCHEDULE_PLAN_FOLDER = "app/data/schedule_plan"

    TEMPLATE_MOZZARELLA_BOILING_PLAN = "app/data/templates/constructor_mozzarella.xlsx"
    TEMPLATE_RICOTTA_BOILING_PLAN = "app/data/templates/constructor_ricotta.xlsx"
    TEMPLATE_MASCARPONE_BOILING_PLAN = "app/data/templates/constructor_mascarpone.xlsx"

    IGNORE_SKU_FILE = "app/data/ignore/ignore_sku.json"
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

    @staticmethod
    def abs_path(local_path):
        return os.path.join(basedir, local_path)


class DebugConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + SQLITE_PATH
    ) + "?check_same_thread=False"


class ProductionConfig(BaseClass):
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + SQLITE_PATH
    ) + "?check_same_thread=False"


configs = {"default": DebugConfig, "production": ProductionConfig, "debug": DebugConfig}
