from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Field
from wtforms.validators import DataRequired

class newTestForm(FlaskForm):
    test_name = StringField("Введите название теста", validators=[DataRequired("")])
    submit = SubmitField("Продолжить")

    def get_placeholder(self, field: Field):
        return field.label.text
