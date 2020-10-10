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
    size = db.Column(db.Float)


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
    pourings = db.relationship('PouringProcess', backref='boiling', lazy='dynamic')
    meltings = db.relationship('MeltingProcess', backref='boiling', lazy='dynamic')
    skus = db.relationship('SKU', backref='boiling', lazy='dynamic')

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
    Процесс упаковки
'''
class PackingProcess(db.Model):
    __tablename__ = 'packings'
    id = db.Column(db.Integer, primary_key=True)
    sku_id = db.Column(db.Integer, db.ForeignKey('skus.id'))
    speed = db.Column(db.Integer)




# class CheeseMaker(db.Model):
#     __tablename__ = 'cheese_makers'
#     id = db.Column(db.Integer, primary_key=True)
#     cheese_maker_name = db.Column(db.String)
#     cheeses = db.relationship('Cheese', backref='cheese_maker', lazy='dynamic')
#
#
# class Cheese(db.Model):
#     __tablename__ = 'cheese'
#     id = db.Column(db.Integer, primary_key=True)
#     cheese_name = db.Column(db.String)
#     leaven_time = db.Column(db.Integer)
#     solidification_time = db.Column(db.Integer)
#     cutting_time = db.Column(db.Integer)
#     draining_time = db.Column(db.Integer)
#     cheese_maker_id = db.Column(db.Integer, db.ForeignKey('cheese_makers.id'))
#     status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
