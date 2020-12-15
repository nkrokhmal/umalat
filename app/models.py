from . import db
import json

sku_boiling = db.Table('sku_boiling',
                       db.Column('boiling_id', db.Integer, db.ForeignKey('boilings.id'), primary_key=True),
                       db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))


sku_boiling_form_factor = db.Table('sku_boiling_form_factor',
                                   db.Column('bff_id', db.Integer, db.ForeignKey('boiling_form_factors.id'), primary_key=True),
                                   db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))


'''
    Таблица SKU. Идет привязка к типам варки
'''


class SKU(db.Model):
    __tablename__ = 'skus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    brand_name = db.Column(db.String)
    weight_netto = db.Column(db.Float)
    weight_form_factor = db.Column(db.Float)
    output_per_ton = db.Column(db.Integer)
    shelf_life = db.Column(db.Integer)
    packing_speed = db.Column(db.Integer, nullable=True)
    packing_reconfiguration = db.Column(db.Integer, nullable=True)
    is_rubber = db.Column(db.Boolean)
    packing_reconfiguration_format = db.Column(db.Integer, nullable=True)
    packer_id = db.Column(db.Integer, db.ForeignKey('packers.id'), nullable=True)
    pack_type_id = db.Column(db.Integer, db.ForeignKey('pack_types.id'), nullable=True)
    form_factor_id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), nullable=True)
    # boilings = db.relationship('Boiling', secondary=sku_boiling)

    @staticmethod
    def generate_links_to_bff():
        try:
            skus = db.session.query(SKU).all()
            bffs = db.session.query(BoilingFormFactor).all()
            for sku in skus:
                if not sku.is_rubber:
                    bff = [x for x in bffs if x.weight == sku.weight_form_factor][0]
                    sku.boiling_form_factors.append(bff)
            db.session.commit()
        except Exception as e:
            print('Exception occurred {}'.format(e))
            db.session.rollback()

    @staticmethod
    def generate_links_to_bff_rubber():
        try:
            skus = db.session.query(SKU).all()
            bffs = db.session.query(BoilingFormFactor).all()
            skus = [x for x in skus if x.is_rubber == True]
            for sku in skus:
                for bff in bffs:
                    sku.boiling_form_factors.append(bff)
            db.session.commit()
        except Exception as e:
            print('Exception occurred {}'.format(e))
            db.session.rollback()

    # def __str__(self):
    #     return super().__str__() + " " + self.name

class BoilingFormFactor(db.Model):
    __tablename__ = 'boiling_form_factors'
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer)
    skus = db.relationship('SKU', secondary=sku_boiling_form_factor, backref='boiling_form_factors')

    @staticmethod
    def generate_boiling_form_factors():
        try:
            skus = db.session.query(SKU).all()
            weights = set([x.weight_form_factor for x in skus])
            for weight in weights:
                bff = BoilingFormFactor(
                    weight=weight
                )
                db.session.add(bff)
            db.session.commit()
        except Exception as e:
            print('Exception occurred {}'.format(e))
            db.session.rollback()


'''
    Таблица форм фактор
'''


class FormFactor(db.Model):
    __tablename__ = 'form_factors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_name = db.Column(db.String)
    priorities = db.relationship('Priority', backref='form_factor', lazy='dynamic')
    skus = db.relationship('SKU', backref='form_factor', lazy='dynamic')


    @staticmethod
    def generate_form_factors():
        try:
            form_factors = {
                'Фиор Ди Латте': 'ФДЛ',
                'Чильеджина': 'ЧЛДЖ',
                'Для пиццы': 'ПИЦЦA',
                'Сулугуни': 'CYЛГ',
                'Моцарелла': 'МОЦ',
                'Качокавалло': 'КАЧКВ'
            }
            for name, short_name in form_factors.items():
                ff = FormFactor(
                    name=name,
                    short_name=short_name
                )
                db.session.add(ff)
            db.session.commit()
        except Exception as e:
            print('Exception occurred {}'.format(e))
            db.session.rollback()


'''
    Приоритеты
'''


class Priority(db.Model):
    __tablename__ = 'priorities'
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer)
    form_factor_id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), nullable=True)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'), nullable=True)


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
            name='Термизатор 1',
            short_cleaning_time=25,
            long_cleaning_time=60
        )
        db.session.add(t)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "short_cleaning_time": self.short_cleaning_time,
            "long_cleaning_time": self.long_cleaning_time
        }


class CheeseType(db.Model):
    __tablename__ = 'cheese_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    output = db.Column(db.Integer)
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'), nullable=True)

    @staticmethod
    def generate_cheese_types():
        type1 = CheeseType(
            name='вода',
            output=1000
        )
        type2 = CheeseType(
            name='соль',
            output=850
        )
        db.session.add(type1)
        db.session.add(type2)
        db.session.commit()


'''
    Параметры варки. Процент, приоритет, наличие лактозы
'''


class Boiling(db.Model):
    __tablename__ = 'boilings'
    id = db.Column(db.Integer, primary_key=True)
    percent = db.Column(db.Float)
    is_lactose = db.Column(db.Boolean)
    ferment = db.Column(db.String)
    skus = db.relationship('SKU', secondary=sku_boiling, backref='boilings')
    priorities = db.relationship('Priority', backref='boiling', lazy='dynamic')
    pouring_id = db.Column(db.Integer, db.ForeignKey('pourings.id'), nullable=True)
    pourings = db.relationship('Pouring', backref='boiling', foreign_keys=pouring_id)
    melting_id = db.Column(db.Integer, db.ForeignKey('meltings.id'), nullable=True)
    meltings = db.relationship('Melting', backref='boiling', foreign_keys=melting_id)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    cheese_type = db.relationship('CheeseType', backref='boiling', lazy='dynamic')

    @staticmethod
    def generate_cheese_types_links():
        boilings = db.session.query(Boiling).all()
        cheese_types = db.session.query(CheeseType).all()
        water = [x for x in cheese_types if x.name == 'вода'][0]
        salt = [x for x in cheese_types if x.name == 'соль'][0]
        for boiling in boilings:
            if boiling.percent > 2.7:
                boiling.cheese_type = water
            else:
                boiling.cheese_type = salt
        db.session.commit()



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
    # todo: melting time should be calculated from the volume amount and speed
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
        for name in ['Ульма', 'Мультиголова', 'Техновак', 'Мультиголова/Комет', 'малый Комет', 'САККАРДО',
                     'САККАРДО другой цех', 'ручная работа']:
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
    skus = db.relationship('SKU', backref='pack_types')

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
    # lines_skus = db.relationship('SKU', backref='lines')
    boiling_line = db.relationship('Boiling', backref='lines')
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
    FormFactor.generate_form_factors()


def init_sku():
    with open('app/data/data.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    boilings = db.session.query(Boiling).all()
    packers = db.session.query(Packer).all()
    form_factors = db.session.query(FormFactor).all()
    try:
        for d in data:
            if d['form_factor'] == 'Фиор ди Латте':
                d['form_factor'] = 'Фиор Ди Латте'
            sku = SKU(
                name=d['name'],
                brand_name=d['brand'],
                form_factor_id=[x.id for x in form_factors if x.name == d['form_factor']][0],
                output_per_ton=d['output'],
                packing_speed=d['packing_speed'],
                shelf_life=int(d['shelf_life']),
                packer_id=[x.id for x in packers if x.name == d['packer'] or x.name == d['packer'].replace(" ", "")][0]
            )
            boiling = [x for x in boilings if (x.percent == float(d['percent'])) and
                       (x.ferment == d['ferment'].capitalize()) and
                       (x.is_lactose == d['is_lactose'])][0]
            sku.boilings.append(boiling)
            db.session.add(sku)
        db.session.commit()
    except Exception as e:
        print('Exception occurred {}'.format(e))
        db.session.rollback()