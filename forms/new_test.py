from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FieldList, SubmitField
from wtforms.validators import DataRequired


class newTestForm(FlaskForm):
    test_name = StringField("Введите название теста",
                            validators=[DataRequired("Введите название теста!")])
    quantite_of_answers = IntegerField("Введите количество вопросов",
                                       validators=[
                                           DataRequired("Введите количество вопросов!")])
    # types_of_answers = FieldList("Типы вопросов")
    submit = SubmitField("Продолжить")
