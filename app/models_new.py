from . import db
import json
import numpy as np
import pandas as pd

from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


from .enum import LineName

# Base = declarative_base()


sku_boiling = db.Table('sku_boiling',
                       db.Column('boiling_id', db.Integer, db.ForeignKey('boilings.id'), primary_key=True),
                       db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))

sku_packer = db.Table('sku_packer',
                       db.Column('packer_id', db.Integer, db.ForeignKey('packers.id'), primary_key=True),
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
    collecting_speed = db.Column(db.Integer, nullable=True)
    packing_speed = db.Column(db.Integer, nullable=True)
    production_by_request = db.Column(db.Boolean)
    packing_by_request = db.Column(db.Boolean)
    boxes = db.Column(db.Integer)

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    pack_type_id = db.Column(db.Integer, db.ForeignKey('pack_types.id'), nullable=True)
    form_factor_id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), nullable=True)


    @property
    def packers_str(self):
        return '/'.join([x.name for x in self.packers])

    @property
    def colour(self):
        COLOURS = {
            'Для пиццы': '#E5B7B6',
            'Моцарелла': '#DAE5F1',
            'Фиор Ди Латте': '#CBC0D9',
            'Чильеджина': '#E5DFEC',
            'Качокавалло': '#F1DADA',
            'Сулугуни': '#F1DADA',
            'Терка': '#FFEBE0',
        }
        if 'Терка' not in self.form_factor.name:
            return COLOURS[self.group.name]
        else:
            return COLOURS['Терка']


class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    output_ton = db.Column(db.Integer)
    pouring_time = db.Column(db.Integer)
    serving_time = db.Column(db.Integer)
    melting_speed = db.Column(db.Integer)
    chedderization_time = db.Column(db.Integer)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    skus = db.relationship('SKU', backref=backref('line', uselist=False, lazy='subquery'))
    form_factors = db.relationship('FormFactor', backref=backref('line', uselist=False, lazy='subquery'))
    boilings = db.relationship('Boiling', backref=backref('line', uselist=False))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @property
    def name_short(self):
        if self.name == LineName.SALT:
            return 'Соль'
        elif self.name == LineName.WATER:
            return 'Вода'
        else:
            return None

    @staticmethod
    def generate_lines():
        mozzarella_department = Department.query.filter_by(name='Моцарельный цех').first()
        for params in [(LineName.SALT, 180, 850, 1020, 30, 30), (LineName.WATER, 240, 1000, 900, 30, 30)]:
            line = Line(
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
        db.session.commit()


class Packer(db.Model):
    __tablename__ = 'packers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    skus = db.relationship('SKU', secondary=sku_packer, backref=backref('packers', lazy='subquery'))
    # skus = db.relationship('SKU', backref=backref('packer', uselist=False, lazy='subquery'))

    @staticmethod
    def generate_packer():
        # for name in ['Ульма', 'Мультиголова', 'Техновак', 'Мультиголова/Комет', 'малый Комет', 'САККАРДО',
        #              'САККАРДО другой цех', 'ручная работа']:
        for name in ['Ульма', 'Мультиголова', 'Техновак', 'Комет', 'малый Комет', 'САККАРДО',
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
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)

    @property
    def boiling_type(self):
        return 'salt' if self.line.name == 'Пицца чиз' else 'water'

    def to_str(self):
        values = [self.percent, self.ferment, '' if self.is_lactose else 'без лактозы']
        values = [str(v) for v in values if v]
        return ', '.join(values)


class BoilingTechnology(db.Model):
    __tablename__ = 'boiling_technologies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    pouring_time = db.Column(db.Integer)
    soldification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    pouring_off_time = db.Column(db.Integer)
    pumping_out_time = db.Column(db.Integer)
    extra_time = db.Column(db.Integer)

    boilings = db.relationship('Boiling', backref=backref('boiling_technology', uselist=False))

    @staticmethod
    def create_name(line, percent, ferment, is_lactose):
        boiling_name = [percent, ferment, '' if is_lactose else 'без лактозы']
        boiling_name = ', '.join([str(v) for v in boiling_name if v])
        return 'Линия {}, {}'.format(line, boiling_name)


class CoolingTechnology(db.Model):
    __tablename__ = 'cooling_technologies'
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String)
    first_cooling_time = db.Column(db.Integer)
    second_cooling_time = db.Column(db.Integer)
    salting_time = db.Column(db.Integer)

    form_factors = db.relationship('FormFactor', backref=backref('default_cooling_technology', uselist=False))

    @property
    def time(self):
        values = [self.first_cooling_time, self.second_cooling_time, self.salting_time]
        values = [v if v is not None else np.nan for v in values]
        return np.nansum(values)

    @staticmethod
    def create_name(form_factor_name):
        return 'Технология охлаждения форм фактора {}'.format(form_factor_name)

    def __repr__(self):
        return 'CoolingTechnology({}, {}, {})'.format(self.first_cooling_time, self.second_cooling_time, self.salting_time)


class Termizator(db.Model):
    __tablename__ = 'termizators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_cleaning_time = db.Column(db.Integer)
    long_cleaning_time = db.Column(db.Integer)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_name = db.Column(db.String)
    form_factors = db.relationship('SKU', backref='group')

    @staticmethod
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
                # 'Терка': 'ТЕРКА'
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


parent_child = db.Table(
    'FormFactorMadeFromMadeTo',
    db.Column('ParentChildId', db.Integer, primary_key=True),
    db.Column('ParentId', db.Integer, db.ForeignKey('form_factors.id')),
    db.Column('ChildId', db.Integer, db.ForeignKey('form_factors.id'))
)


class FormFactor(db.Model):
    __tablename__ = 'form_factors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    relative_weight = db.Column(db.Integer)
    default_cooling_technology_id = db.Column(db.Integer, db.ForeignKey('cooling_technologies.id'), nullable=True)
    skus = db.relationship('SKU', backref=backref('form_factor', uselist=False, lazy='subquery'))
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)

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

    @property
    def weight_with_line(self):
        if self.line:
            return '{}: {}'.format(self.line.name_short, self.relative_weight)
        else:
            return '{}'.format(self.name)

    @property
    def full_name(self):
        return '{}, {}'.format('Форм фактор', self.name)

