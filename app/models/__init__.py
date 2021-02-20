from .. import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import func, extract


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    batch_numbers = db.relationship('BatchNumber', backref=backref('department', uselist=False,),)
    lines = db.relationship('Line', backref=backref('department', uselist=False,),)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class SKU(db.Model):
    __tablename__ = 'skus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    brand_name = db.Column(db.String)
    weight_netto = db.Column(db.Float)
    shelf_life = db.Column(db.Integer)
    collecting_speed = db.Column(db.Integer, nullable=True)
    packing_speed = db.Column(db.Integer, nullable=True)
    in_box = db.Column(db.Integer)

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    form_factor_id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), nullable=True)
    pack_type_id = db.Column(db.Integer, db.ForeignKey('pack_types.id'), nullable=True)

    type = db.Column(db.String)
    __mapper_args__ = {
        'polymorphic_identity': 'skus',
        'polymorphic_on': type
    }

    @property
    def packers_str(self):
        return '/'.join([x.name for x in self.packers])


class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    output_ton = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    skus = db.relationship('SKU', backref=backref('line', uselist=False, lazy='subquery'))
    form_factors = db.relationship('FormFactor', backref=backref('line', uselist=False, lazy='subquery'))
    boilings = db.relationship('Boiling', backref=backref('line', uselist=False))
    steam_consumption = db.relationship('SteamConsumption', backref=backref('line', uselist=False))
    washer = db.relationship('Washer', backref=backref('line', uselist=False, lazy='subquery'))

    type = db.Column(db.String)
    __mapper_args__ = {
        'polymorphic_identity': 'lines',
        'polymorphic_on': type
    }

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Washer(db.Model):
    __tablename__ = 'washer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    time = db.Column(db.Integer)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    short_name = db.Column(db.String)

    skus = db.relationship('SKU', backref='group')


parent_child = db.Table(
    'FormFactorMadeFromMadeTo',
    db.Column('ParentChildId', db.Integer, primary_key=True),
    db.Column('ParentId', db.Integer, db.ForeignKey('form_factors.id')),
    db.Column('ChildId', db.Integer, db.ForeignKey('form_factors.id')),
)


class FormFactor(db.Model):
    __tablename__ = 'form_factors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    relative_weight = db.Column(db.Integer)
    skus = db.relationship('SKU', backref=backref('form_factor', uselist=False, lazy='subquery'))
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)

    made_from = relationship(
        'FormFactor',
        secondary=parent_child,
        primaryjoin=id == parent_child.c.ChildId,
        secondaryjoin=id == parent_child.c.ParentId,
        backref=backref('made_to')
    )

    type = db.Column(db.String)
    __mapper_args__ = {
        'polymorphic_identity': 'form_factors',
        'polymorphic_on': type
    }

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


sku_boiling = db.Table('sku_boiling',
                       db.Column('boiling_id', db.Integer, db.ForeignKey('boilings.id'), primary_key=True),
                       db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))


class Boiling(db.Model):
    __tablename__ = 'boilings'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    boiling_technology_id = db.Column(db.Integer, db.ForeignKey('boiling_technologies.id'), nullable=True)

    skus = db.relationship('SKU', secondary=sku_boiling, backref='made_from_boilings')

    type = db.Column(db.String)
    __mapper_args__ = {
        'polymorphic_identity': 'boilings',
        'polymorphic_on': type
    }


class BoilingTechnology(db.Model):
    __tablename__ = 'boiling_technologies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    boilings = db.relationship('Boiling', backref=backref('boiling_technology', uselist=False))

    type = db.Column(db.String)
    __mapper_args__ = {
        'polymorphic_identity': 'boiling_technologies',
        'polymorphic_on': type
    }


sku_packer = db.Table('sku_packer',
                       db.Column('packer_id', db.Integer, db.ForeignKey('packers.id'), primary_key=True),
                       db.Column('sku_id', db.Integer, db.ForeignKey('skus.id'), primary_key=True))


class Packer(db.Model):
    __tablename__ = 'packers'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    skus = db.relationship('SKU', secondary=sku_packer, backref=backref('packers', lazy='subquery'))

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


class SteamConsumption(db.Model):
    __tablename__ = 'steam_consumption'
    id = db.Column(db.Integer, primary_key=True)
    params = db.Column(db.String)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)


class BatchNumber(db.Model):
    __tablename__ = 'batch_number'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Date)
    beg_number = db.Column(db.Integer)
    end_number = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    @staticmethod
    def last_batch_number(date):
        last_batch = db.session.query(BatchNumber)\
            .filter(func.DATE(BatchNumber.datetime) < date.date())\
            .filter(extract('month', BatchNumber.datetime) == date.month)\
            .filter(extract('year', BatchNumber.datetime) == date.year)\
            .order_by(BatchNumber.datetime.desc())\
            .first()
        if last_batch is not None:
            return last_batch.end_number
        else:
            return 0

    @staticmethod
    def get_batch_by_date(date):
        return db.session.query(BatchNumber)\
            .filter(func.DATE(BatchNumber.datetime) == date.date())\
            .first()


from .mozzarella import *
from .ricotta import *
from .mascarpone import *
from .cream_cheese import *

