from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, Field, FieldList, Label
from wtforms.validators import DataRequired

class newTestForm(FlaskForm):
    test_name = StringField("Введите название теста", validators=[DataRequired("")])
    quantite_of_answers = IntegerField("Введите количество вопросов", validators=[DataRequired("")])
    # types_of_answers = FieldList(Label(field_id=0, text="Типы вопросов"))
    submit = SubmitField("Продолжить")

    def get_placeholder(self, field: Field):
        return field.label.text
