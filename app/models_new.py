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
    skus = db.relationship('SKU', backref=backref('line', uselist=False))
    boilings = db.relationship('Boiling', backref=backref('line', uselist=False))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @staticmethod
    def generate_lines():
        mozzarella_department = Department.query.filter_by(name='Моцарельный цех').first()
        for params in [(LineName.SALT, 180, 850, 1020, 30, 30), (LineName.WATER, 240, 1000, 800, 30, 30)]:
            line = Line(
                name=params[0],
                chedderization_time=params[1],
                output_per_ton=params[2],
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
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)


class BoilingTechnology(db.Model):
    __tablename__ = 'boiling_technologies'
    id = db.Column(db.Integer, primary_key=True)
    pouring_time = db.Column(db.Integer)
    soldification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    pouring_off_time = db.Column(db.Integer)
    extra_time = db.Column(db.Integer)

    boilings = db.relationship('Boiling', backref=backref('boiling_technology', uselist=False))


class CoolingTechnology(db.Model):
    __tablename__ = 'cooling_technologies'
    id = db.Column(db.Integer, primary_key=True)
    first_cooling_time = db.Column(db.Integer)
    second_cooling_time = db.Column(db.Integer)
    salting_time = db.Column(db.Integer)

    form_factors = db.relationship('FormFactor', backref=backref('default_cooling_technology', uselist=False))


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
    form_factors = db.relationship('FormFactor', backref='group')

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
                'Терка': 'ТЕРКА'
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
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    default_cooling_technology_id = db.Column(db.Integer, db.ForeignKey('cooling_technologies.id'), nullable=True)
    skus = db.relationship('SKU', backref=backref('form_factor', uselist=False))

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

