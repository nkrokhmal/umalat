from . import db


'''
    На всякий случай таблица со статусами
'''
class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String)
    # cheeses = db.relationship('Cheese', backref='roles', lazy='dynamic')


'''
    Таблица SKU. Идет привязка к типам варки
'''
class SKU(db.Model):
    __tablename__ = 'skus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'))

    # todo: delete (now in Pack)
    size = db.Column(db.Float) # Размер упаковки
    # выход в кг с одной варки # todo: put into Line (water = 1000, pizza cheese = 850). Сделать лучше на одну тонну только (water = 125, pizza cheese = 106.25)
    output_per_boiling = db.Column(db.Integer)
    # срок годности
    shelf_life = db.Column(db.Integer)
    # Скорость фасовки
    # todo: rename to packing_speed
    speed = db.Column(db.Integer)
    # время быстрой смены пленки
    packing_reconfiguration = db.Column(db.Integer)
    # время смены формата пленки
    packing_reconfiguration_format = db.Column(db.Integer)
    # связка с фасовщиком
    packing_id = db.Column(db.Integer, db.ForeignKey('packings.id'), nullable=True)

    # связка с линиями
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)

    # todo: add ferment - закваска
    # todo: add Pack, FormFactor
    # todo: add brand_name

'''
    Параметры термизатора.
'''
class Termizator(db.Model):
    __tablename__ = 'termizators'
    id = db.Column(db.Integer, primary_key=True)
    short_cleaning_time = db.Column(db.Integer)
    long_cleaning_time = db.Column(db.Integer)
    # todo: add pouring_time


'''
    Параметры варки. Процент, приоритет, наличие лактозы
'''
class Boiling(db.Model):
    __tablename__ = 'boilings'
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer)
    percent = db.Column(db.Float)
    is_lactose = db.Column(db.Boolean)
    skus = db.relationship('SKU', backref='boiling', lazy='dynamic')
    pouring_id = db.Column(db.Integer, db.ForeignKey('pourings.id'), nullable=True)
    pourings = db.relationship('PouringProcess', backref='boiling', foreign_keys=pouring_id)
    melting_id = db.Column(db.Integer, db.ForeignKey('meltings.id'), nullable=True)
    meltings = db.relationship('MeltingProcess', backref='boiling', foreign_keys=melting_id)

    @staticmethod
    def generate_boilings():
        for percent in [2.7, 3.3, 3.6]:
            for is_lactose in [True, False]:
                b = Boiling(
                    percent=percent,
                    priority=0,
                    is_lactose=is_lactose)
                db.session.add(b)
        db.session.commit()


'''
    Описание сыроизготовителя
'''
class CheeseMakers(db.Model):
    __tablename__ = 'cheesemakers'
    id = db.Column(db.Integer, primary_key=True)
    cheese_maker_name = db.Column(db.String)
    type = db.Column(db.String)

    # todo: add possible volumes: [6,7,8]

class GlobalPouringProcess(db.Model):
    __tablename__ = 'global_pouring_processes'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)
'''
    Описание процесса налива
'''
# todo: unify naming
class PouringProcess(db.Model):
    __tablename__ = 'pourings'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)
    soldification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    # todo: что это за время?
    pouring_off_time = db.Column(db.Integer)
    extra_time = db.Column(db.Integer)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'))


'''
    Процесс плавления
'''
# todo: unify naming
class MeltingProcess(db.Model):
    __tablename__ = 'meltings'
    id = db.Column(db.Integer, primary_key=True)
    serving_time = db.Column(db.Integer)
    melting_time = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    first_cooling_time = db.Column(db.Integer)
    second_cooling_time = db.Column(db.Integer)
    salting_time = db.Column(db.Integer)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'))


'''
    Фасовщики
'''
# todo: rename to Packer
class Packing(db.Model):
    __tablename__ = 'packings'
    id = db.Column(db.Integer, primary_key=True)
    # todo: make string?
    name = db.Column(db.Integer)
    packing_skus = db.relationship('SKU', backref='packing')

    @staticmethod
    def generate_packings():
        for name in ['Ульма', 'Мультиголова', 'Техновак', 'Мультиголова/Комета', 'малый Комет', 'САККАРДО',
                     'Ручная работа']:
            packing = Packing(name=name)
            db.session.add(packing)
        db.session.commit()


'''
    Форм-фактор
'''
# todo: make form
class FormFactor(db.Model):
    __tablename__ = 'formfactors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    size = db.Column(db.Float)
    freezing_time = db.Column(db.Integer)


'''
    Упаковка
'''
# todo: make form
class Pack(db.Model):
    __tablename__ = 'packs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    weight_netto = db.Column(db.Float)
    pack_type = db.Column(db.String) # флоупак, пластиковый лоток, термоформаж, пластиковый стакан

'''
    Линии
'''
class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer)
    lines_skus = db.relationship('SKU', backref='lines')

    # todo: add cheddarization time (4 for salted, 3 for water)

    @staticmethod
    def generate_lines():
        for name in ['Пицца чиз', 'Моцарелла в воде']:
            line = Line(name=name)
            db.session.add(line)
        db.session.commit()



# '''
#     Описание цехов
# '''
# class Departmenent(db.Model):
#     __tablename__ = 'departments'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#
#
# '''
#     Описание линий
# '''
# class DepartmentLines(db.Model):
#     __tablename__ = 'department_lines'
#     id = db.Column(db.Integer, primary_key=True)

