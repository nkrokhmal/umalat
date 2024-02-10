import collections

from app.enum import DepartmentName, LineName
from app.globals import db
from app.models.adygea import AdygeaLine
from app.models.basic import Department, Group, Packer, PackType, User, Washer
from app.models.brynza import BrynzaLine
from app.models.butter import ButterLine
from app.models.mascarpone import MascarponeLine
from app.models.milk_project import MilkProjectLine
from app.models.mozzarella import MozzarellaLine


def generate_user():
    user = User(
        username="umalat",
        email="umalat@mail.ru",
        password="1",
    )
    db.session.add(user)
    db.session.commit()


def generate_departments():
    for name in [
        "Моцарельный цех",
        "Рикоттный цех",
        DepartmentName.MASCARPONE,
        "Масло цех",
        "Милкпроджект",
        "Адыгейский цех",
    ]:
        department = Department(name=name)
        db.session.add(department)
    db.session.commit()


def generate_group():
    try:
        groups = {
            "Фиор Ди Латте": "ФДЛ",
            "Чильеджина": "ЧЛДЖ",
            "Для пиццы": "ПИЦЦА",
            "Сулугуни": "CYЛГ",
            "Моцарелла": "МОЦ",
            "Качокавалло": "КАЧКВ",
            "Масса": "МАССА",
            "Рикотта": "РКТ",
            "Маскарпоне": "МСКП",
            "Кремчиз": "КРМ",
            "Творожный": "ТВР",
            "Робиола": "РБЛ",
            "Сливки": "СЛВ",
            "Масло": "МСЛ",
            "Четук": "ЧТК",
            "Качорикотта": "КЧРКТ",
            "Кавказский": "КВК",
            "Черкесский": "ЧРКС",
            "Брынза": "БРНЗ",
            "Чанах": "ЧНХ",
        }
        for name, short_name in groups.items():
            ff = Group(name=name, short_name=short_name)
            db.session.add(ff)
        db.session.commit()
    except Exception as e:
        print("Exception occurred {}".format(e))
        db.session.rollback()


def generate_packer():
    for name in [
        "Ульма",
        "Мультиголова",
        "Техновак",
        "Комет",
        "малый Комет",
        "САККАРДО",
        "САККАРДО другой цех",
        "ручная работа",
        "Сипак",
    ]:
        packer = Packer(name=name)
        db.session.add(packer)
    db.session.commit()


def generate_pack_types():
    for name in ["флоупак", "пластиковый лоток", "термоформаж", "пластиковый стакан"]:
        pack_type = PackType(name=name)
        db.session.add(pack_type)
    db.session.commit()


def generate_mozzarella_lines():

    mozzarella_department = Department.query.filter_by(name="Моцарельный цех").first()
    for params in [
        (LineName.SALT, 180, 960, 8300, 1020, 30, 30),
        (LineName.WATER, 240, 1100, 8300, 900, 30, 30),
    ]:
        line = MozzarellaLine(
            name=params[0],
            chedderization_time=params[1],
            output_kg=params[2],
            input_ton=params[3],
            serving_time=params[5],
            pouring_time=params[6],
        )
        if mozzarella_department is not None:
            line.department_id = mozzarella_department.id
        db.session.add(line)

    mascarpone_department = Department.query.filter_by(name=DepartmentName.MASCARPONE).first()

    butter_department = Department.query.filter_by(name="Масло цех").first()
    butter_line = ButterLine(
        name="Масло",
        output_kg=450,
        preparing_time=70,
        displacement_time=10,
        # cleaning_time=27*5,
        cleaning_time=100,
        boiling_volume=900,
    )
    butter_line.department_id = butter_department.id
    db.session.add(butter_line)

    milk_project_department = Department.query.filter_by(name="Милкпроджект").first()
    milk_project_line = MilkProjectLine(
        name="Милкпроджект",
        water_collecting_time=20,
        equipment_check_time=10,
    )
    milk_project_line.department_id = milk_project_department.id
    db.session.add(milk_project_line)

    adygea_department = Department.query.filter_by(name="Адыгейский цех").first()
    adygea_line = AdygeaLine(
        name=LineName.ADYGEA,
        lunch_time=30,
        preparation_time=60,
    )
    adygea_line.department_id = adygea_department.id
    db.session.add(adygea_line)

    db.session.commit()


def generate_washer():
    WasherData = collections.namedtuple("WasherData", "name, time")
    mozzarella_department = Department.query.filter_by(name="Моцарельный цех").first()
    adygea_department = Department.query.filter_by(name="Адыгейский цех").first()

    for data in [
        WasherData("Короткая мойка термизатора", 25),
        WasherData("Длинная мойка термизатора", 80),
    ]:
        washer = Washer(
            name=data.name,
            time=data.time,
            department_id=mozzarella_department.id,
        )
        db.session.add(washer)

    for data in [
        WasherData("adygea_cleaning", 120),
    ]:
        washer = Washer(
            name=data.name,
            time=data.time,
            department_id=adygea_department.id,
        )
        db.session.add(washer)

    db.session.commit()


def generate_all():
    generate_user()
    generate_departments()
    generate_group()
    generate_packer()
    generate_pack_types()
    generate_mozzarella_lines()
    generate_washer()
