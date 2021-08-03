from app.imports.external import *

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

    BOILING_PLAN_FOLDER = "boiling_plan"
    APPROVED_FOLDER = "approved"
    SCHEDULE_FOLDER = "schedule"
    SCHEDULE_DICT_FOLDER = "schedule_dict"
    TASK_FOLDER = "task"

    BATCH_NUMBERS_DIR = "db/batch_numbers"
    DYNAMIC_DIR = "app/data/dynamic"
    UPLOAD_TMP_FOLDER = "app/data/dynamic/tmp"
    SKU_PLAN_FOLDER = "app/data/dynamic/sku_plan"

    TEMPLATE_MOZZARELLA_BOILING_PLAN = (
        "app/data/static/templates/constructor_mozzarella.xlsx"
    )
    TEMPLATE_RICOTTA_BOILING_PLAN = "app/data/static/templates/constructor_ricotta.xlsx"
    TEMPLATE_MASCARPONE_BOILING_PLAN = (
        "app/data/static/templates/constructor_mascarpone.xlsx"
    )
    TEMPLATE_BUTTER_BOILING_PLAN = "app/data/static/templates/constructor_butter.xlsx"
    TEMPLATE_MILKPROJECT_BOILING_PLAN = (
        "app/data/static/templates/constructor_milk_project.xlsx"
    )
    TEMPLATE_SCHEDULE_PLAN = "app/data/static/templates/constructor_schedule.xlsx"
    TEMPLATE_ADYGEA_BOILING_PLAN = "app/data/static/templates/constructor_adygea.xlsx"

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
        "Кавказский": "#E5B7B6",
        "Черкесский": "#CBC0D9",
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

    TELEGRAM_BOT_TOKEN = "1101281504:AAEbWzUXem-FK7Yb2RHvkg-h8sMilZAuFpA"
    TELEGRAM_CHAT_ID = -544068496
    TELEGRAM_CHAT_FILES_ID = -541375793

    RQ_REDIS_URL = "redis://redis:6379/0"
    RQ_QUEUES = ["default"]

    @staticmethod
    def abs_path(local_path):
        return os.path.join(basedir, local_path)

    DEPARTMENT_NAMES = {
        "mozzarella": "моцарелла",
        "mascarpone": "маскарпоне",
        "milk_project": "милкпроджект",
        "butter": "масло",
        "adygea": "адыгейский",
        "contour_cleanings": "контурные мойки",
        "ricotta": "рикотта",
    }

    EMPTY_ALLOWED_DEPARTMENTS = [
        "mascarpone",
        "milk_project",
        "butter",
        "adygea",
        "contour_cleanings",
    ]


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
    TEST_MILKPROJECT = "app/data/tests/milk_project_plan.xlsx"
    TEST_BUTTER = "app/data/tests/butter_plan.xlsx"
    TEST_ADYGEA = "app/data/tests/adygea_plan.xlsx"

    TELEGRAM_BOT_TOKEN = "1101281504:AAEbWzUXem-FK7Yb2RHvkg-h8sMilZAuFpA"
    TELEGRAM_CHAT_ID = -544068496
    TELEGRAM_CHAT_FILES_ID = -541375793


configs = {
    "default": DebugConfig,
    "production": ProductionConfig,
    "debug": DebugConfig,
    "test": TestConfig,
}

DEFAULT_ENVIRONMENT = "debug"
ENVIRONMENT = os.environ.get("ENVIRONMENT", DEFAULT_ENVIRONMENT)
config = configs[ENVIRONMENT]
