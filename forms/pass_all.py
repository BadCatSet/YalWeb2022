from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, widgets, SelectMultipleField


class PassStartForm(FlaskForm):
    submit = SubmitField('Начать прохождение')


class TaskInputForm(FlaskForm):
    answer = StringField('Ответ')
    submit = SubmitField('Сохранить')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def get_task_choice_form(fields):
    class TaskChoiceForm(FlaskForm):
        task_choice = RadioField('Label', choices=list(zip(fields, fields)))
        submit = SubmitField('Сохранить')

    return TaskChoiceForm


def get_task_multy_choice_form(fields):
    class TaskMultyChoiceForm(FlaskForm):
        task_choice = MultiCheckboxField(choices=fields)

        submit = SubmitField('Сохранить')

    return TaskMultyChoiceForm
