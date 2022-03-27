from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField('Логин', validators=[DataRequired('Пустой логин')])
    password = PasswordField('Пароль', validators=[DataRequired('Пустой пароль')])
    submit = SubmitField('Войти')
