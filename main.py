import datetime
import sqlite3

from flask import Flask, redirect, render_template
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from db import sql_gate
from forms.login import LoginForm
from forms.signup import SignupForm


class User:
    is_active = True
    is_anonymous = False

    def __init__(self, _id):
        data = sql_gate.get_users(con, _id=_id)
        if len(data) == 0:
            self.is_authenticated = False
        else:
            self.is_authenticated = True
            self.id, self.email, self.password_h, self.username = data[0]

    def get_id(self):
        return self.id

    def __str__(self):
        return f'username:{self.username} ' \
               f'email:{self.email} ' \
               f'auth:{self.is_authenticated} '


app = Flask(__name__)
app.config['SECRET_KEY'] = 'password_is_eight_asterisks'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    return render_template('index.html', title='YalWeb2022')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = sql_gate.get_users(con, email=form.data['email'], password=form.data['password'])
        if len(user):
            login_user(User(user[0][0]), remember=True)
            return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        data = sql_gate.get_users(con, email=form.data['email'])
        if len(data) != 0:
            form.email.errors.append('почта уже занята!')
        else:
            sql_gate.add_user(con, form.data['email'], form.data['password'])
    return render_template('signup.html', title='Регистрация', form=form)


if __name__ == '__main__':
    con = sqlite3.connect('db/db.db', check_same_thread=False)
    app.run()
    print(current_user)  # no use, just for non-grey import
