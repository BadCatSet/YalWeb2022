from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField


class PassStartForm(FlaskForm):
    submit = SubmitField('Начать прохождение')


class TaskInputForm(FlaskForm):
    answer = StringField('Ответ')
    submit = SubmitField('Сохранить')


def get_task_choice_form(fields):
    class TaskChoiceForm(FlaskForm):
        task_choice = RadioField('Label', choices=list(zip(fields, fields)))
        submit = SubmitField('Сохранить')

    return TaskChoiceForm
