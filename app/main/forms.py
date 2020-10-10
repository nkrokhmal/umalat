from flask_restplus import ValidationError
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.validators import Required
from flask_wtf import FlaskForm
from ..models import MeltingProcess, Boiling
from .. import db


class MeltingProcess(FlaskForm):
    percent = FloatField('Enter percentage', validators=[Required()])
    priority = IntegerField('Enter priority', validators=[Required()])
    is_lactose = BooleanField('Enter is lactose', validators=[Required()])
    submit = SubmitField('Submit')


class SKUForm(FlaskForm):
    name = StringField('Enter SKU name', validators=[Required()])
    size = FloatField('Enter packing size', validators=[Required()])
    percent = SelectField('Choose percent', coerce=int)
    is_lactose = SelectField('Choose is lactose', coerce=int)
    boilings = None
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)
        self.boilings = db.session.query(Boiling).all()
        self.percent.choices = list(enumerate(set([x.percent for x in self.boilings])))
        self.is_lactose.choices = list(enumerate(set([x.is_lactose for x in self.boilings])))


class CheeseForm(FlaskForm):
    cheese_name = StringField('Cheese name', validators=[Required()])
    leaven_time = IntegerField('Leaven time in minutes', validators=[Required()])
    solidification_time = IntegerField('Solidification time in minutes', validators=[Required()])
    cutting_time = IntegerField('Cutting time in minutes', validators=[Required()])
    draining_time = IntegerField('Draining time in minutes', validators=[Required()])
    cheese_maker = SelectField('Cheese maker', coerce=int)
    submit = SubmitField('Submit')

    # def __init__(self, *args, **kwargs):
    #     super(CheeseForm, self).__init__(*args, **kwargs)
    #     self.cheese_maker.choices = [(cm.id, cm.cheese_maker_name) for cm in
    #                                  db.session.query(CheeseMaker).order_by(CheeseMaker.cheese_maker_name).all()]


class CheeseMakerForm(FlaskForm):
    cheese_maker_name = StringField('Name of cheese maker', validators=[Required()])
    submit = SubmitField('Submit')
