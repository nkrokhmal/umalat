import flask_wtf
import wtforms
from wtforms.validators import DataRequired


class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField('Username', id='username_login', validators=[DataRequired()])
    password = wtforms.PasswordField('Password', id='pwd_login', validators=[DataRequired()])
