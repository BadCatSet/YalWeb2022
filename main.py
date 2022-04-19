import datetime
import json
import logging
import os
from logging import critical, debug, error, info, warning
import sqlite3
from typing import Any

from flask import Flask, redirect, render_template, flash, request
from flask_login import LoginManager, current_user, login_required, login_user, \
    logout_user

from db import sql_gate
from forms.login import LoginForm
from forms.new_test import newTestForm
from forms.pass_all import PassStartForm, TaskInputForm
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


class PassError(AppError):
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


class Task:
    actual_version: int

    def __init__(self, data, score, version):

        if version != self.actual_version:
            data = self.update_data_version(data, version)

        self.__dict__.update(data)
        self.score = score

    # сделаю по мере необходимости в конкретных заданиях, так же нужна функция для обновления данных в бд
    def update_data_version(self, content, version):
        while version != self.actual_version:
            version += 1
        return content

    def __repr__(self):
        return str(self.__dict__)


class TaskInput(Task):
    actual_version = 1


class Test:
    task_dict = {}

    # task_dict = {'input': TaskInput}

    def __init__(self, test_id):
        self.test_id = test_id
        self.tasks = []
        self.max_score = 0

        with open(f'tests_data/{test_id}.json', encoding='utf-8') as file:
            data = json.load(file)
        version = data['version']
        content = data['content']

        for i in content:
            self.handle_task(i, version)

    def handle_task(self, data, version):
        task_data = data['task']
        task_type = data['type']
        score = data['score']

        self.max_score += score

        task = self.task_dict[task_type]
        self.tasks.append(task(task_data, score, version))

    def match_id(self, other_test_id):
        return self.test_id == other_test_id

    def get_task(self, number):
        return self.tasks[number]

    def task_names(self):
        return list(map(lambda x: int(x) + 1, range(len(self.tasks))))


class SavedAnswer:
    def __init__(self, task):
        self.task = task
        self.answer: Any = None

    def set(self, answer):
        self.answer = answer

    def get_score(self):
        return self.task.score * (self.task.correct_answer == self.answer)

    def __repr__(self):
        return f'SavedAnswer for:\ntask: {self.task}\nanswer: {self.answer}'


@login_manager.user_loader
def load_user(user_id):
    user_data = sql_gate.get_users(con, user_id=user_id)[0]
    return User(user_data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/personal_account', methods=['POST', 'GET'])
# @login_required
def personal_account():
    file_oldname = os.path.join("static/img", f'{current_user.get_id()}.png')
    file_newname_newfile = os.path.join("static/img", "photo.png")
    if request.method == 'GET':
        if f'static/img/{current_user.get_id()}.png' in os.listdir('static/img'):
            os.rename(file_oldname, file_newname_newfile)
            return render_template('personal_account.html', title='YalWeb2022', flag=True)
        else:
            return render_template('personal_account.html', title='YalWeb2022', flag=False)

    elif request.method == 'POST':
        f = request.files['file']
        f.save(f'static/img/{current_user.get_id()}.png')
        os.rename(file_oldname, file_newname_newfile)
        return render_template('personal_account.html', title='YalWeb2022', flag=True,
                               name=f'static/img/{current_user.get_id()}.png')
    os.rename(file_newname_newfile, file_oldname)

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
    if not current_user.is_authenticated:
        return redirect('/login')
    form = PassStartForm()
    if form.validate_on_submit():
        return redirect(f'/pass/{test_id}/1')

    return render_template('pass_start.html',
                           tilte='Начало теста',
                           form=form)


@app.route('/pass/<int:test_id>/<int:exercise_number>', methods=['GET', 'POST'])
def pass_handler(test_id, exercise_number):
    exercise_number -= 1
    if not current_user.is_authenticated:
        return redirect('/login')
    item_id = current_user.get_id(), test_id, exercise_number

    if test_id not in loaded_tests:
        loaded_tests[test_id] = Test(test_id)
    current_test = loaded_tests[test_id]

    if item_id not in saved_answers:
        saved_answers[item_id] = SavedAnswer(current_test.get_task(exercise_number))
    task_names = current_test.task_names()

    if isinstance(loaded_tests[test_id].get_task(exercise_number), TaskInput):
        return pass_input(test_id, exercise_number, task_names)


def pass_input(test_id, exercise_number, task_names):
    item_id = current_user.get_id(), test_id, exercise_number

    form = TaskInputForm()
    if form.validate_on_submit():
        answer = form.data['answer']  # TODO
        saved_answers[item_id].set(answer)

    task = loaded_tests[test_id].get_task(exercise_number)

    return render_template('pass_input.html',
                           title='тест',
                           condition=task.text,
                           form=form,
                           task_names=task_names,
                           test_id=test_id)


@app.route("/pass/<int:test_id>/complete")
def pass_complete(test_id):
    user_id = current_user.get_id()
    max_score = loaded_tests[test_id].max_score
    real_score = 0
    for _, s in filter(lambda x: x[0][0] == user_id and x[0][1] == test_id, saved_answers.items()):
        real_score += s.get_score()
    sql_gate.add_result(con, user_id, test_id, real_score, max_score)
    return redirect('/')


@app.route("/test_creator", methods=['GET', 'POST'])
# @login_required
def test_creator_start():
    form = newTestForm()
    if form.validate_on_submit():
        if form.test_name.data == '':
            flash('Название теста не может быть пустым!')
        else:
            return redirect('/test_creator/1')
    return render_template('test_creator_start.html',
                           tilte='Конфигурация теста',
                           form=form)


@app.route('/test_creator/<int:exercise>', methods=['GET', 'POST'])
# @login_required
def test_creator(exercise: int):
    return render_template('test_creator.html', title=f"Создание теста/вопрос {exercise}")


if __name__ == '__main__':
    loaded_tests = {}  # {test_id: Test}
    saved_answers = {}  # {(user_id, test_id): {exercise_number: answer}}
    # dict[(int, int):dict[int:SavedAnswer]]

    loaded_tests: dict[int, Test] = dict()  # {test_id: Test}
    saved_answers: dict[tuple[int, int, int], SavedAnswer] = dict()  # {(user_id, test_id, exercise_number):  answer}

    info('connecting to database...')
    con = sqlite3.connect('db/db.db', check_same_thread=False)
    info('...connected successful')

    app.run()
    _ = current_user, debug, info, warning, error, critical  # просто так надо
