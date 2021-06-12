from app.models import *


def generate_user():
    user = User(
        username='umalat',
        email='umalat@mail.ru',
        password='1',
    )
    db.session.add(user)
    db.session.commit()


def generate_departments():
    for name in ["Моцарельный цех", "Рикоттный цех", "Маскарпоновый цех", "Масло цех", "Милкпроджект"]:
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
            "Качорикотта": "КЧРКТ"
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
        (LineName.SALT, 180, 850, 8000, 1020, 30, 30),
        (LineName.WATER, 240, 1000, 8000, 900, 30, 30),
    ]:
        line = MozzarellaLine(
            name=params[0],
            chedderization_time=params[1],
            output_ton=params[2],
            input_ton=params[3],
            melting_speed=params[4],
            serving_time=params[5],
            pouring_time=params[6],
        )
        if mozzarella_department is not None:
            line.department_id = mozzarella_department.id
        db.session.add(line)

    ricotta_department = Department.query.filter_by(name="Рикоттный цех").first()
    ricotta_line = RicottaLine(
        name="Рикотта",
        input_ton=1850,
    )
    ricotta_line.department_id = ricotta_department.id
    db.session.add(ricotta_line)

    mascarpone_department = Department.query.filter_by(name="Маскарпоновый цех").first()
    mascarpone_line = MascarponeLine(name="Маскарпоне")
    mascarpone_line.department_id = mascarpone_department.id
    db.session.add(mascarpone_line)

    butter_department = Department.query.filter_by(name="Масло цех").first()
    butter_line = ButterLine(
        name="Масло",
        output_ton=450,
        preparing_time=70,
        displacement_time=10,
    )
    butter_line.department_id = butter_department.id
    db.session.add(butter_line)

    milk_project_department = Department.query.filter_by(name="Милкпроджект").first()
    milk_project_line = MilkProjectLine(
        name="Милкпроджект"
    )
    milk_project_line.department_id = milk_project_department.id
    db.session.add(milk_project_line)

    db.session.commit()


def generate_washer():
    WasherData = collections.namedtuple("WasherData", "name, time")
    mozzarella_department = Department.query.filter_by(name="Моцарельный цех").first()
    mascarpone_department = Department.query.filter_by(name="Маскарпоновый цех").first()
    ricotta_department = Department.query.filter_by(name="Рикоттный цех").first()
    for data in [
        WasherData("Короткая мойка термизатора", 40),
        WasherData("Длинная мойка термизатора", 80),
    ]:
        washer = Washer(
            name=data.name,
            time=data.time,
            department_id=mozzarella_department.id,
        )
        db.session.add(washer)

    for data in [
        WasherData("sourdough", 13),
        WasherData("sourdough_cream_cheese", 12),
        WasherData("separator", 15),
        WasherData("heat_exchanger", 12),
        WasherData("homogenizer", 12),
    ]:
        washer = Washer(
            name=data.name,
            time=data.time,
            department_id=mascarpone_department.id,
        )
        db.session.add(washer)

    for data in [
        WasherData("bath_cleaning_1", 2),
        WasherData("bath_cleaning_2", 4),
        WasherData("bath_cleaning_3", 1),
        WasherData("bath_cleaning_4", 2),
        WasherData("bath_cleaning_5", 2),
        WasherData("container_cleaning_1", 12),
        WasherData("container_cleaning_2", 12),
        WasherData("container_cleaning_3", 12),
    ]:
        washer = Washer(
            name=data.name,
            time=data.time,
            department_id=ricotta_department.id,
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
