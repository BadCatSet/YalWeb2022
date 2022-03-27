from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class SignupForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired('Пустая почта')])
    username = StringField('Имя пользователя', validators=[DataRequired('Пустое имя пользователя')])
    password1 = PasswordField('Пароль', validators=[DataRequired('Пустой пароль')])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired('Пустой пароль'),
                                                              EqualTo('password1', 'Пароли разные')])
    submit = SubmitField('Войти')
