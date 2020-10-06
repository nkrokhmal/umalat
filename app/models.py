from . import db


class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String)
    cheeses = db.relationship('Cheese', backref='roles', lazy='dynamic')


class CheeseMaker(db.Model):
    __tablename__ = 'cheese_makers'
    id = db.Column(db.Integer, primary_key=True)
    cheese_maker_name = db.Column(db.String)
    cheeses = db.relationship('Cheese', backref='cheese_maker', lazy='dynamic')


class Cheese(db.Model):
    __tablename__ = 'cheese'
    id = db.Column(db.Integer, primary_key=True)
    cheese_name = db.Column(db.String)
    leaven_time = db.Column(db.Integer)
    solidification_time = db.Column(db.Integer)
    cutting_time = db.Column(db.Integer)
    draining_time = db.Column(db.Integer)
    cheese_maker_id = db.Column(db.Integer, db.ForeignKey('cheese_makers.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
