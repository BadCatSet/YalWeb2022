from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, Field, StringField
from wtforms.validators import DataRequired

TYPES_OF_QUESTIONS = (
    "Ввод ответа в текстовой или числовой форме",
    "Выбор из нескольких вариантов ответа",
    "Выбор нескольких вариантов из списка"
)

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
