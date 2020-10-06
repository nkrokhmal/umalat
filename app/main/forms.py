from flask_restplus import ValidationError
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import Required
from flask_wtf import FlaskForm
from ..models import CheeseMaker
from .. import db


class CheeseForm(FlaskForm):
    cheese_name = StringField('Cheese name', validators=[Required()])
    leaven_time = IntegerField('Leaven time in minutes', validators=[Required()])
    solidification_time = IntegerField('Solidification time in minutes', validators=[Required()])
    cutting_time = IntegerField('Cutting time in minutes', validators=[Required()])
    draining_time = IntegerField('Draining time in minutes', validators=[Required()])
    cheese_maker = SelectField('Cheese maker', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CheeseForm, self).__init__(*args, **kwargs)
        self.cheese_maker.choices = [(cm.id, cm.cheese_maker_name) for cm in
                                     db.session.query(CheeseMaker).order_by(CheeseMaker.cheese_maker_name).all()]


class CheeseMakerForm(FlaskForm):
    cheese_maker_name = StringField('Name of cheese maker', validators=[Required()])
    submit = SubmitField('Submit')
