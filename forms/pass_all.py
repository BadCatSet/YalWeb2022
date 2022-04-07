from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class PassStartForm(FlaskForm):
    submit = SubmitField('Начать прохождение')


class PassSimpleForm(FlaskForm):
    answer = StringField('Ответ')
    submit = SubmitField('Войти')
