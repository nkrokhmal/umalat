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
    # Размер упаковки
    size = db.Column(db.Float)
    # Скорость фасовки
    speed = db.Column(db.Integer)
    # срок годности
    shelf_life = db.Column(db.Integer)
    # время быстрой смены пленки
    packing_reconfiguration = db.Column(db.Integer)
    # время смены формата пленки
    packing_reconfiguration_format = db.Column(db.Integer)
    # связка с фасовщиком
    packing_id = db.Column(db.Integer, db.ForeignKey('packings.id'), nullable=True)


'''
    Параметры термизатора.
'''
class Termizator(db.Model):
    __tablename__ = 'termizators'
    id = db.Column(db.Integer, primary_key=True)
    short_cleaning_time = db.Column(db.Integer)
    long_cleaning_time = db.Column(db.Integer)


'''
    Параметры варки. Процент, приоритет, наличие лактозы
'''
class Boiling(db.Model):
    __tablename__ = 'boilings'
    id = db.Column(db.Integer, primary_key=True)
    percent = db.Column(db.Float)
    priority = db.Column(db.Integer)
    is_lactose = db.Column(db.Boolean)
    skus = db.relationship('SKU', backref='boiling', lazy='dynamic')
    pouring_id = db.Column(db.Integer, db.ForeignKey('pourings.id'), nullable=True)
    pourings = db.relationship('PouringProcess', backref='boiling', foreign_keys=pouring_id)
    melting_id = db.Column(db.Integer, db.ForeignKey('meltings.id'), nullable=True)
    meltings = db.relationship('MeltingProcess', backref='boiling', foreign_keys=melting_id)

    @staticmethod
    def generate_boilings():
        for percent in [2.8, 3.3, 3.6]:
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


class GlobalPouringProcess(db.Model):
    __tablename__ = 'global_pouring_processes'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)


'''
    Описание процесса налива
'''
class PouringProcess(db.Model):
    __tablename__ = 'pourings'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)
    soldification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    pouring_off_time = db.Column(db.Integer)
    extra_time = db.Column(db.Integer)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'))


'''
    Процесс плавления
'''
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
class Packing(db.Model):
    __tablename__ = 'packings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer)
    packing_skus = db.relationship('SKU', backref='packing')

    @staticmethod
    def generate_packings():
        for name in ['Ульма', 'Мультиголова', 'Техновак', 'Мультиголова/Комета', 'малый Комет', 'САККАРДО',
                     'Ручная работа']:
            packing = Packing(name=name)
            db.session.add(packing)
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

