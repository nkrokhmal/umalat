from . import *


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