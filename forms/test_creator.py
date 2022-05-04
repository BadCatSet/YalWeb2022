from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, Field, StringField
from wtforms.validators import DataRequired

TYPES_OF_QUESTIONS = (
    "Выбор 1 из нескольких",
    "Ввод текста"
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
    submit = SubmitField("Продолжить")

    def get_placeholder(self, field: Field):
        return field.label.text


class NewQuestionForm(FlaskForm):
    typeOfTest = SelectField(validators=[DataRequired("")], choices=TYPES_OF_QUESTIONS)
    submit = SubmitField("Продолжить")

    def get_placeholder(self, field: Field):
        return field.label.text


class SimpleComboBoxQuestionForm(FlaskForm):
    def get_placeholder(self, field: Field):
        return field.label.text
