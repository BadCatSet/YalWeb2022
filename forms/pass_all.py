from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class PassStartForm(FlaskForm):
    submit = SubmitField('Начать прохождение')


class TaskInputForm(FlaskForm):
    answer = StringField('Ответ')
    submit = SubmitField('Сохранить')
