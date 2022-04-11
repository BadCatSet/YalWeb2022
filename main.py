import datetime
import json
import logging
from logging import critical, debug, error, info, warning
import sqlite3

from flask import Flask, redirect, render_template
from flask_login import LoginManager, current_user, login_required, login_user, \
    logout_user

from db import sql_gate
from forms.login import LoginForm
from forms.new_test import newTestForm
from forms.pass_all import PassStartForm
from forms.signup import SignupForm

logging.basicConfig(
    filename='log.log',
    format='%(levelname)s %(asctime)s %(name)s >>> %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
    encoding='utf-8')
info('--- starting app -----------------------------------------')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'password_is_eight_asterisks'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)


class AppError(Exception):
    pass


class User:
    is_active = True
    is_anonymous = False

    def __init__(self, data):
        debug(f'creating user object with {data}')

        if not isinstance(data, tuple):
            err = f'user object must receive a tuple not {type(data)}'
            error(err)
            raise AppError('err')

        if len(data) == 0:
            self.is_authenticated = False
        else:
            self.is_authenticated = True
            self.id, self.email, self.password_h, self.username = data

    def get_id(self):
        return self.id

    def __str__(self):
        return f'''username:{self.username}    
        email:{self.email}    
        auth:{self.is_authenticated}'''


class Test:
    def __init__(self, test_id):
        self.test = sql_gate.get_test(con, test_id)


class PassSimpleTask:
    actual_version = 1

    def __init__(self, raw_data):
        data = json.loads(raw_data)
        version = data['version']
        content = data['content']
        if version != self.actual_version:
            content = self.update_content_version(content, version)

        self.condition = content['text']
        self.question = content['question']
        self.answer = content['answer']
        self.answer_type = content['answer_type']

    # сделаю по мере необходимости, так же нужна функция для обновления данных в бд
    def update_content_version(self, content, version):
        while version != self.actual_version:
            version += 1
        return content


class SavedAnswer:
    def __init__(self, task, score):
        self.task = task
        self.score = score
        self.answer = None


@login_manager.user_loader
def load_user(user_id):
    user_data = sql_gate.get_users(con, user_id=user_id)[0]
    return User(user_data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    return render_template('index.html',
                           title='YalWeb2022')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = sql_gate.get_users(con, email=form.data['email'],
                                  password=form.data['password'])
        if len(user):
            login_user(User(user[0]), remember=True)
            return redirect('/')
    return render_template('login.html',
                           title='Авторизация',
                           form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        data = sql_gate.get_users(con, email=form.data['email'])
        if len(data) != 0:
            form.email.errors.append('почта уже занята!')
        else:
            sql_gate.add_user(con, form.data['email'], form.data['password1'])
    return render_template('signup.html',
                           title='Регистрация',
                           form=form)


@app.route('/pass/<int:test_id>', methods=['GET', 'POST'])
def pass_start(test_id):
    form = PassStartForm()
    if form.validate_on_submit():
        item_id = current_user.get_id(), test_id
        saved_answers[item_id] = saved_answers.get(item_id, {})

        return redirect(f'/pass/{test_id}/1')
    return render_template('pass_start.html',
                           tilte='Начало теста',
                           form=form)


@app.route('/pass/<int:test_id>/<int:exercise>', methods=['GET', 'POST'])
def pass_handler(test_id, exercise_number):
    item_id = current_user.get_id(), test_id
    if exercise_number not in list(saved_answers[item_id]):
        saved_answers[item_id][exercise_number] = SavedAnswer()
    answer = saved_answers[item_id][exercise_number]
    if answer is None:
        pass


@app.route("/pass_creator_start", methods=['GET', 'POST'])
def pass_creator_start():
    form = newTestForm()
    if form.validate_on_submit():
        return redirect('/pass_creator/1')
    return render_template('pass_start.html',
                           tilte='Начало теста',
                           form=form,
                           info="Создание теста")


@app.route('/pass_creator/<int:exercise>', methods=['GET', 'POST'])
def pass_creator(exercise: int):
    return render_template('pass_creator_start.html',
                           title=f"Создание теста/вопрос {exercise}")


if __name__ == '__main__':
    loaded_tests = {}  # {test_id: Test}
    saved_answers = {}  # {(user_id, test_id): {exercise_number: answer}} dict[(int, int):dict[int:SavedAnswer]]

    info('connecting to database...')
    con = sqlite3.connect('db/db.db', check_same_thread=False)
    info('...connected successful')

    app.run()

    _ = current_user, debug, info, warning, error, critical  # просто так надо
