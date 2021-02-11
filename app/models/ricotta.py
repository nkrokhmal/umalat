from .. import db
from sqlalchemy.orm import relationship, backref
from . import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology


class RicottaSKU(SKU):
    __tablename__ = 'ricotta_skus'
    __mapper_args__ = {'polymorphic_identity': 'ricotta_skus'}

    id = db.Column(db.Integer, db.ForeignKey('skus.id'), primary_key=True)


class RicottaLine(Line):
    __tablename__ = 'ricotta_lines'
    __mapper_args__ = {'polymorphic_identity': 'ricotta_lines'}

    id = db.Column(db.Integer, db.ForeignKey('lines.id'), primary_key=True)


class RicottaFormFactor(FormFactor):
    __tablename__ = 'ricotta_form_factors'
    __mapper_args__ = {'polymorphic_identity': 'ricotta_form_factor'}

    id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), primary_key=True)


class RicottaBoiling(Boiling):
    __tablename__ = 'ricotta_boilings'
    __mapper_args__ = {'polymorphic_identity': 'ricotta_boiling'}

    id = db.Column(db.Integer, db.ForeignKey('boilings.id'), primary_key=True)
    boiling_type = db.Column(db.String)

    analysis = db.relationship('RicottaAnalysis', backref=backref('boiling', uselist=False, lazy='subquery'))


class RicottaBoilingTechnology(BoilingTechnology):
    __tablename__ = 'ricotta_boiling_technologies'
    __mapper_args__ = {'polymorphic_identity': 'ricotta_boiling_technology'}

    id = db.Column(db.Integer, db.ForeignKey('boiling_technologies.id'), primary_key=True)
    heating_time = db.Column(db.Integer)
    delay_time = db.Column(db.Integer)
    protein_harvest_time = db.Column(db.Integer)
    pumping_out_time = db.Column(db.Integer)


class RicottaAnalysis(db.Model):
    __tablename__ = 'ricotta_analyses'
    id = db.Column(db.Integer, primary_key=True)
    preparation = db.Column(db.Integer)
    analysis = db.Column(db.Integer)
    pumping = db.Column(db.Integer)

    boiling_id = db.Column(db.Integer, db.ForeignKey('ricotta_boilings.id'), nullable=True)








