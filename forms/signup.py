from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class SignupForm(FlaskForm):
    email = StringField('Логин', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password1 = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Войти')
