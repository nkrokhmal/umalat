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
    # название бренда
    brand_name = db.Column(db.String)
    # весс нетто
    weight_netto = db.Column(db.Float)
    # вес одного шарика
    weight_form_factor = db.Column(db.Float)
    # выход в кг с одной тонны воды
    output_per_ton = db.Column(db.Integer)
    # срок годности
    shelf_life = db.Column(db.Integer)
    # Скорость фасовки
    packing_speed = db.Column(db.Integer)
    # время быстрой смены пленки
    packing_reconfiguration = db.Column(db.Integer)
    # время смены формата пленки
    packing_reconfiguration_format = db.Column(db.Integer)
    # связка с фасовщиком
    packer_id = db.Column(db.Integer, db.ForeignKey('packers.id'), nullable=True)
    # связка с линиями
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    # связка с типом упаковки
    pack_type_id = db.Column(db.Integer, db.ForeignKey('pack_types.id'), nullable=True)


'''
    Параметры термизатора.
'''
class Termizator(db.Model):
    __tablename__ = 'termizators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_cleaning_time = db.Column(db.Integer)
    long_cleaning_time = db.Column(db.Integer)
    pouring_time = db.Column(db.Integer)

    @staticmethod
    def generate_termizator():
        t = Termizator(
            name='Termizator 1',
            short_cleaning_time=25,
            long_cleaning_time=60
        )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "short_cleaning_time": self.short_cleaning_time,
            "long_cleaning_time": self.long_cleaning_time
        }


'''
    Параметры варки. Процент, приоритет, наличие лактозы
'''
class Boiling(db.Model):
    __tablename__ = 'boilings'
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer)
    percent = db.Column(db.Float)
    is_lactose = db.Column(db.Boolean)
    ferment = db.Column(db.String)
    skus = db.relationship('SKU', backref='boiling', lazy='dynamic')
    pouring_id = db.Column(db.Integer, db.ForeignKey('pourings.id'), nullable=True)
    pourings = db.relationship('Pouring', backref='boiling', foreign_keys=pouring_id)
    melting_id = db.Column(db.Integer, db.ForeignKey('meltings.id'), nullable=True)
    meltings = db.relationship('Melting', backref='boiling', foreign_keys=melting_id)

    @staticmethod
    def generate_boilings():
        for percent in [2.7, 3.3, 3.6]:
            for is_lactose in [True, False]:
                for ferment in ['Альче', 'Сакко']:
                    b = Boiling(
                        ferment=ferment,
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
    possible_volumes = db.Column(db.String)


class GlobalPouringProcess(db.Model):
    __tablename__ = 'global_pouring_processes'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)


'''
    Описание процесса налива
'''
class Pouring(db.Model):
    __tablename__ = 'pourings'
    id = db.Column(db.Integer, primary_key=True)
    # Время налива
    pouring_time = db.Column(db.Integer)
    # Время затвердевания
    soldification_time = db.Column(db.Integer)
    # Время нарезки
    cutting_time = db.Column(db.Integer)
    # Время слива
    pouring_off_time = db.Column(db.Integer)
    # Дополнительное время
    extra_time = db.Column(db.Integer)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'))


'''
    Процесс плавления
'''
class Melting(db.Model):
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
class Packer(db.Model):
    __tablename__ = 'packers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    packer_skus = db.relationship('SKU', backref='packer')

    @staticmethod
    def generate_packer():
        for name in ['Ульма', 'Мультиголова', 'Техновак', 'Мультиголова/Комета', 'малый Комет', 'САККАРДО',
                     'Ручная работа']:
            packer = Packer(name=name)
            db.session.add(packer)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


'''
    Типы упаковок
'''
class PackType(db.Model):
    __tablename__ = 'pack_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    @staticmethod
    def generate_types():
        for name in ['флоупак', 'пластиковый лоток', 'термоформаж', 'пластиковый стакан']:
            pack_type = PackType(
                name=name
            )
            db.session.add(pack_type)
        db.session.commit()

'''
    Линии
'''
class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer)
    lines_skus = db.relationship('SKU', backref='lines')
    cheddarization_time = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    @staticmethod
    def generate_lines():
        mozzarella_department = Departmenent.query.filter_by(name='Моцарельный цех').first()
        for params in [('Пицца чиз', 3), ('Моцарелла в воде', 4)]:
            line = Line(name=params[0], cheddarization_time=params[1])
            if mozzarella_department is not None:
                line.department_id = mozzarella_department.id
            db.session.add(line)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


# '''
#     Описание цехов
# '''
class Departmenent(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @staticmethod
    def generate_departments():
        for name in ['Моцарельный цех']:
            department = Departmenent(
                name=name
            )
            db.session.add(department)
        db.session.commit()


def init_all():
    Departmenent.generate_departments()
    Line.generate_lines()
    PackType.generate_types()
    Packer.generate_packer()
    Boiling.generate_boilings()
    Termizator.generate_termizator()



