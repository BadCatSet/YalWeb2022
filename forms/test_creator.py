from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, Field, StringField, SelectMultipleField, \
    widgets
from wtforms.validators import DataRequired

TYPES_OF_QUESTIONS = {
    "input": "Ввод ответа в текстовой или числовой форме",
    "choice": "Выбор из нескольких вариантов ответа",
    "multy_choice": "Выбор нескольких вариантов из списка"
}

SUBJECTS = (
    "Программирование",
    "Математика",
    "Русский язык",
    "Литература",
    "Физика",
    "Химия",
    "Биология",
    "География",
    "История",

)


class NewTestForm(FlaskForm):
    test_name = StringField("Введите название теста", validators=[DataRequired("")])
    subject = SelectField("Выберите предмет теста", validators=[DataRequired("")],
                          choices=SUBJECTS)
    type_of_test = SelectField("Выберите тип вопроса", validators=[DataRequired("")],
                               choices=TYPES_OF_QUESTIONS)
    submit = SubmitField("Продолжить")

    def get_placeholder(self, field: Field):
        return field.label.text

    def __init__(self, questions: int, **kwargs):
        super().__init__(**kwargs)
        self.question_buttons = []
        for i in range(1, questions + 1):
            self.question_buttons.append(SelectField(str(i)))


class MultiSubmitField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.SubmitInput()


def get_editor_input_form(number_of_tasks: int, number_of_fields: int, task_type: str):
    attrs = dict()
    for i in range(number_of_tasks):
        attrs[f'task_button_{i}'] = SubmitField(str(i))
    for i in range(number_of_fields):
        attrs[f'field_{i}'] = StringField()
    attrs['num_buttons'] = number_of_tasks
    attrs['task_type'] = task_type
    attrs['submit'] = SubmitField('Сохранить')
    res = type("TaskMultyChoiceForm", (FlaskForm,), attrs)
    return res
