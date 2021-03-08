# from .. import db
# import numpy as np
# import datetime
# from sqlalchemy.orm import relationship, backref
# from sqlalchemy import func, extract
#
#
# class Department(db.Model):
#     __tablename__ = 'departments'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     lines = db.relationship('Line', backref=backref('department', uselist=False))
