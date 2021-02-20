from app.models import *
from collections import namedtuple


def generate_departments():
    for name in ['Моцарельный цех', 'Рикоттный цех', 'Маскарпоновый цех']:
        department = Department(
            name=name
        )
        db.session.add(department)
    db.session.commit()


def generate_group():
    try:
        groups = {
            'Фиор Ди Латте': 'ФДЛ',
            'Чильеджина': 'ЧЛДЖ',
            'Для пиццы': 'ПИЦЦА',
            'Сулугуни': 'CYЛГ',
            'Моцарелла': 'МОЦ',
            'Качокавалло': 'КАЧКВ',
            'Масса': 'МАССА',
            'Рикотта': 'РКТ',
            'Маскарпоне': 'МСКП',
        }
        for name, short_name in groups.items():
            ff = Group(
                name=name,
                short_name=short_name
            )
            db.session.add(ff)
        db.session.commit()
    except Exception as e:
        print('Exception occurred {}'.format(e))
        db.session.rollback()


def generate_packer():
    for name in ['Ульма', 'Мультиголова', 'Техновак', 'Комет', 'малый Комет', 'САККАРДО',
                 'САККАРДО другой цех', 'ручная работа']:
        packer = Packer(name=name)
        db.session.add(packer)
    db.session.commit()


def generate_pack_types():
    for name in ['флоупак', 'пластиковый лоток', 'термоформаж', 'пластиковый стакан']:
        pack_type = PackType(
            name=name
        )
        db.session.add(pack_type)
    db.session.commit()


def generate_mozzarella_lines():
    mozzarella_department = Department.query.filter_by(name='Моцарельный цех').first()
    for params in [(LineName.SALT, 180, 850, 1020, 30, 30), (LineName.WATER, 240, 1000, 900, 30, 30)]:
        line = MozzarellaLine(
            name=params[0],
            chedderization_time=params[1],
            output_ton=params[2],
            melting_speed=params[3],
            serving_time=params[4],
            pouring_time=params[5],
        )
        if mozzarella_department is not None:
            line.department_id = mozzarella_department.id
        db.session.add(line)

    ricotta_department = Department.query.filter_by(name='Рикоттный цех').first()
    line = RicottaLine(
        name='Рикотта',
        output_ton=1650,
    )
    line.department_id = ricotta_department.id
    db.session.add(line)

    db.session.commit()


def generate_washer():
    WasherData = namedtuple('WasherData', 'name, time')
    for data in [WasherData('Короткая мойка термизатора', 40),
                 WasherData('Длинная мойка термизатора', 80)]:
        washer = Washer(
            name=data.name,
            time=data.time,
        )
        db.session.add(washer)
    db.session.commit()


def generate_all():
    generate_departments()
    generate_group()
    generate_packer()
    generate_pack_types()
    generate_mozzarella_lines()
    generate_washer()