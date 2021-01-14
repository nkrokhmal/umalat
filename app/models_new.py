from . import db
import json
import numpy as np
import pandas as pd

from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


sku_boiling = db.Table('sku_boiling',
                       db.Column('boiling_id', db.Integer, db.ForeignKey('boilings.id'), primary_key=True),
                       db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    lines = db.relationship('Line', backref=backref('department', uselist=False))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @staticmethod
    def generate_departments():
        for name in ['Моцарельный цех']:
            department = Department(
                name=name
            )
            db.session.add(department)
        db.session.commit()


class SKU(db.Model):
    __tablename__ = 'skus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    brand_name = db.Column(db.String)
    weight_netto = db.Column(db.Float)
    shelf_life = db.Column(db.Integer)
    packing_speed = db.Column(db.Integer, nullable=True)

    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    packer_id = db.Column(db.Integer, db.ForeignKey('packers.id'), nullable=True)
    pack_type_id = db.Column(db.Integer, db.ForeignKey('pack_types.id'), nullable=True)
    form_factor_id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), nullable=True)


class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    output_per_ton = db.Column(db.Integer)
    pouring_time = db.Column(db.Integer)
    serving_time = db.Column(db.Integer)
    melting_speed = db.Column(db.Integer)
    chedderization_time = db.Column(db.Integer)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    skus = db.relationship('SKU', backref=backref('line', uselist=False), lazy='dynamic')
    boilings = db.relationship('Boiling', backref=backref('line', uselist=False), lazy='dynamic')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @staticmethod
    def generate_lines():
        mozzarella_department = Department.query.filter_by(name='Моцарельный цех').first()
        for params in [('Пицца чиз', 180, 850, 1020, 30), ('Моцарелла в воде', 240, 1000, 800, 30)]:
            line = Line(
                name=params[0],
                chedderization_time=params[1],
                output_per_ton=params[2],
                melting_speed=params[3],
                serving_time=params[4]
            )
            if mozzarella_department is not None:
                line.department_id = mozzarella_department.id
            db.session.add(line)
        db.session.commit()


class Packer(db.Model):
    __tablename__ = 'packers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    packer_skus = db.relationship('SKU', backref=backref('packer', uselist=False))

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


class PackType(db.Model):
    __tablename__ = 'pack_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    skus = db.relationship('SKU', backref=backref('pack_type', uselist=False))

    @staticmethod
    def generate_types():
        for name in ['флоупак', 'пластиковый лоток', 'термоформаж', 'пластиковый стакан']:
            pack_type = PackType(
                name=name
            )
            db.session.add(pack_type)
        db.session.commit()


class Boiling(db.Model):
    __tablename__ = 'boilings'
    id = db.Column(db.Integer, primary_key=True)
    percent = db.Column(db.Float)
    is_lactose = db.Column(db.Boolean)
    ferment = db.Column(db.String)
    skus = db.relationship('SKU', secondary=sku_boiling, backref='made_from_boilings')

    boiling_technology_id = db.Column(db.Integer, db.ForeignKey('boiling_technologies.id'), nullable=True)
    boiling_technologies = db.relationship('BoilingTechnology', backref='boiling', foreign_keys=boiling_technology_id)

    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)


class BoilingTechnology(db.Model):
    __tablename__ = 'boiling_technologies'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)
    soldification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    pouring_off_time = db.Column(db.Integer)
    extra_time = db.Column(db.Integer)

    boilings = db.relationship('Boiling', backref=backref('boiling_technology', uselist=False), lazy='dynamic')


class Termizator(db.Model):
    __tablename__ = 'termizators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_cleaning_time = db.Column(db.Integer)
    long_cleaning_time = db.Column(db.Integer)
    pouring_time = db.Column(db.Integer)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_name = db.Column(db.String)
    form_factors = db.relationship('FormFactor', backref='group', lazy='dynamic')

    @staticmethod
    def generate_group():
        try:
            groups = {
                'Фиор Ди Латте': 'ФДЛ',
                'Чильеджина': 'ЧЛДЖ',
                'Для пиццы': 'ПИЦЦA',
                'Сулугуни': 'CYЛГ',
                'Моцарелла': 'МОЦ',
                'Качокавалло': 'КАЧКВ',
                'Масса': 'МАССА'
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


form_factor_link = db.Table('form_factor_link',
                            db.Column('form_factor_id', db.Integer, db.ForeignKey('form_factors.id'), primary_key=True),
                            db.Column('made_from_id', db.Integer, db.ForeignKey('form_factors.id'), primary_key=True))

parent_child = db.Table(
    'ParentChild',
    Base.metadata,
    db.Column('ParentChildId', db.Integer, primary_key=True),
    db.Column('ParentId', db.Integer, db.ForeignKey('FormFactor.Id')),
    db.Column('ChildId', db.Integer, db.ForeignKey('FormFactor.Id'))
)


class FormFactor(db.Model):
    __tablename__ = 'form_factors'
    id = db.Column(db.Integer, primary_key=True)
    relative_weight = db.Column(db.Integer)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    skus = db.relationship('SKU', backref=backref('form_factor', uselist=False), lazy='dynamic')

    made_from = relationship(
        'FormFactor',
        secondary=parent_child,
        primaryjoin=id == parent_child.c.ChildId,
        secondaryjoin=id == parent_child.c.ParentId,
        backref=backref('made_to')
    )

    def add_made_from(self, ff):
        if ff not in self.made_from:
            self.made_from.append(ff)


def fill_db():
    fill_simple_data()
    fill_boiling_technologies()
    fill_boiling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()


def fill_simple_data():
    Department.generate_departments()
    Line.generate_lines()
    Packer.generate_packer()
    PackType.generate_types()
    Group.generate_group()


def fill_boiling_technologies():
    path = 'app/data/params.xlsx'
    df = pd.read_excel(path, index_col=0)
    boiling_technologies_columns = ['Время налива', 'Время отвердевания', 'Время нарезки', 'Время слива',
                                    'Дополнительное время']
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict('records')
    for bt in bt_data:
        technology = BoilingTechnology(
            pouring_time=bt['Время налива'],
            soldification_time=bt['Время отвердевания'],
            cutting_time=bt['Время нарезки'],
            pouring_off_time=bt['Время слива'],
            extra_time=bt['Дополнительное время']
        )

        db.session.add(technology)
        db.session.commit()


def fill_boilings():
    lines = db.session.query(Line).all()
    bts = db.session.query(BoilingTechnology).all()
    path = 'app/data/params.xlsx'
    df = pd.read_excel(path, index_col=0)
    columns = ['Тип закваски', 'Процент', 'Наличие лактозы', 'Линия',
               'Время налива', 'Время отвердевания', 'Время нарезки', 'Время слива',
               'Дополнительное время']
    b_data = df[columns]
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict('records')
    for b in b_data:
        if b['Линия'] == 'Соль':
            line_id = [x for x in lines if x.name == 'Пицца чиз'][0].id
        else:
            line_id = [x for x in lines if x.name == 'Моцарелла в воде'][0].id
        bt_id = [x for x in bts if (x.pouring_time == b['Время налива']) &
                 (x.soldification_time == b['Время отвердевания']) &
                 (x.cutting_time == b['Время нарезки']) &
                 (x.pouring_off_time == b['Время слива']) &
                 (x.extra_time == b['Дополнительное время'])][0].id
        boiling = Boiling(
            percent=b['Процент'],
            is_lactose=True if b['Наличие лактозы'] == 'Да' else False,
            ferment=b['Тип закваски'],
            boiling_technology_id=bt_id,
            line_id=line_id
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    groups = db.session.query(Group).all()
    mass = [x for x in groups if x.name == 'Масса'][0].id
    mass_ff = FormFactor(
        relative_weight=100000,
        group_id=mass
    )
    db.session.add(mass_ff)
    db.session.commit()

    path = 'app/data/params.xlsx'
    df = pd.read_excel(path, index_col=0)
    columns = ['Вес форм фактора', 'Название форм фактора']
    ff_data = df[columns]
    ff_data = ff_data.drop_duplicates()
    ff_data = ff_data.to_dict('records')
    for ff in ff_data:
        group_id = [x for x in groups if x.name == ff['Название форм фактора']][0].id
        form_factor = FormFactor(
            relative_weight=ff['Вес форм фактора'],
            group_id=group_id
        )
        db.session.add(form_factor)
    db.session.commit()

    form_factors = db.session.query(FormFactor).all()
    mass_ff = [x for x in form_factors if x.relative_weight == 100000][0]
    for form_factor in form_factors:
        form_factor.add_made_from(form_factor)
        form_factor.add_made_from(mass_ff)
    db.session.commit()


def fill_sku():
    lines = db.session.query(Line).all()
    packer = db.session.query(Packer).all()
    boilings = db.session.query(Boiling).all()
    path = 'app/data/params.xlsx'
    df = pd.read_excel(path, index_col=0)
    columns = ['Название SKU', 'Процент', 'Наличие лактозы', 'Тип закваски', 'Имя бренда', 'Вес нетто', 'Срок хранения',
               'Является ли SKU теркой', 'Упаковщик', 'Скорость упаковки', 'Линия']
    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict('records')
    for sku in sku_data:
        is_lactose = True if sku['Наличие лактозы'] == 'Да' else False
        add_sku = SKU(
            name=sku['Название SKU'],
            brand_name=sku['Имя бренда'],
            weight_netto=sku['Вес нетто'],
            shelf_life=sku['Срок хранения'],
            packing_speed=sku['Скорость упаковки']
        )
        add_sku.packer_id = [x.id for x in packer if x.name == sku['Упаковщик']][0]
        if sku['Линия'] == 'Соль':
            line_id = [x for x in lines if x.name == 'Пицца чиз'][0].id
        else:
            line_id = [x for x in lines if x.name == 'Моцарелла в воде'][0].id
        boiling = [x for x in boilings if
                   (x.percent == sku['Процент']) &
                   (x.is_lactose == is_lactose) &
                   (x.ferment == sku['Тип закваски']) &
                   (x.line_id == line_id)][0]
        add_sku.made_from_boilings.append(boiling)
        add_sku.line_id = line_id
        db.session.add(add_sku)
    db.session.commit()








