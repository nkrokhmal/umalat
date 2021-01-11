from . import db
import json
import numpy as np

sku_boiling = db.Table('sku_boiling',
                       db.Column('boiling_id', db.Integer, db.ForeignKey('boilings.id'), primary_key=True),
                       db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    lines = db.relationship('Line', backref='departments')


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
    skus = db.relationship('SKU', backref='lines')


class Packer(db.Model):
    __tablename__ = 'packers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    packer_skus = db.relationship('SKU', backref='packer')


class PackType(db.Model):
    __tablename__ = 'pack_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    skus = db.relationship('SKU', backref='pack_types')


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
    boiling_id = db.Column(db.Integer, db.ForeignKey('boilings.id'))


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
    form_factors = db.Column(db.Integer, db.ForeignKey('form_factors.id'))


form_factor_link = db.Table('form_factor_link',
                             db.Column('form_factor_id', db.Integer, db.ForeignKey('form_factors.id'), primary_key=True),
                             db.Column('made_from_id', db.Integer, db.ForeignKey('form_factors.id'), primary_key=True))

class FormFactor(db.Model):
    __tablename__ = 'form_factors'
    id = db.Column(db.Integer, primary_key=True)
    relative_weight = db.Column(db.Integer)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    made_from_id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), nullable=True)
    made_from = db.relationship(
        'FormFactor',
        backref=db.backref('form_factor_link', lazy='dynamic'),
        secondary=form_factor_link,
        primaryjoin=(form_factor_link.c.form_factor_id == id),
        secondaryjoin=(form_factor_link.c.made_from_id == id),
        lazy='dynamic'
    )
    # made_from = db.relationship('FormFactor', backref=db.backref('made_from', remote_side=[id]))

    # followers = db.Table('followers',
    #                      db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    #                      db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    #                      )
    # followed = db.relationship(
    #     'User', secondary=followers,
    #     primaryjoin=(followers.c.follower_id == id),
    #     secondaryjoin=(followers.c.followed_id == id),
    #     backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


