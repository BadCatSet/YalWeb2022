import datetime
import json

import logging
from logging import debug, error, info
import os
import sqlite3
from typing import Any, Literal

from flask import Flask, redirect, render_template, request

from flask_login import LoginManager, current_user, login_required, login_user, \
    logout_user

from db import sql_gate

from forms.login import LoginForm
from forms.pass_all import PassStartForm, TaskInputForm, get_task_choice_form, get_task_multy_choice_form
from forms.signup import SignupForm
from forms.test_creator import NewTestForm, SUBJECTS

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
    correct_answer: Any

    def __init__(self, data, score, version):

        if version != self.actual_version:
            data = self.update_data_version(data, version)

        self.__dict__.update(data)
        self.score = score

    # сделаю по мере необходимости в конкретных заданиях,
    # так же нужна функция для обновления данных в бд
    def update_data_version(self, content, version):
        while version != self.actual_version:
            version += 1
        return content

    def get_empty_answer(self):
        raise NotImplementedError

    def __repr__(self):
        return '<Task:' + str(self.__dict__) + '>'


class TaskInput(Task):
    actual_version = 1
    text: str
    answer_type: Literal['int', 'float', 'str']
    correct_answer: int | float | str

    def get_empty_answer(self):
        return ''


class TaskChoice(Task):
    actual_version = 1
    text: str
    items: list[str]
    correct_answer: str

    def __init__(self, data, score, version):
        super().__init__(data, score, version)
        self.form = get_task_choice_form(tuple(self.items))

    def get_empty_answer(self):
        return self.items[0]


class TaskMultyChoice(Task):
    actual_version = 1
    text: str
    items: list[str]
    correct_answer: list[str]

    def __init__(self, data, score, version):
        super().__init__(data, score, version)
        self.form = get_task_multy_choice_form(tuple(self.items))

    def get_empty_answer(self):
        return list()


class Test:
    _loaded = {}
    task_dict = {'input': TaskInput, 'choice': TaskChoice, 'multy_choice': TaskMultyChoice}

    def __new__(cls, test_id: int = 'new_test'):
        if test_id == 'new_test':
            test_id = sql_gate.add_test(con, owner_id=current_user.get_id())

            with open(f'./tests_data/{test_id}.json', 'wb') as file, \
                    open(f'./tests_data/empty.json', 'rb') as empty:
                file.write(empty.read())

        if (test := cls._loaded.get(test_id)) is not None:
            return test
        test = super().__new__(cls)
        cls._loaded[test_id] = test
        test._init_from_file(test_id)
        return test

    def _init_from_file(self, test_id):
        data = sql_gate.get_tests(con, test_id)
        self.name = data[0][2]
        self.test_id = test_id
        self.tasks: list[Task] = []
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

    def get_task(self, number) -> Any:
        return self.tasks[number]

    def task_names(self):
        ln = len(self.tasks)
        return range(1, ln + 1)


class SavedAnswer:
    _loaded = {}

    def __new__(cls, test_id, exercise_number, user_id):
        item_id = test_id, exercise_number, user_id
        if (res := cls._loaded.get(item_id)) is not None:
            return res

        res = super().__new__(cls)
        cls._loaded[item_id] = res
        res.__init__(test_id, exercise_number, user_id)
        return res

    def __init__(self, test_id, exercise_number, user_id):
        if self.__dict__.get('answer') is not None:
            return
        self.test_id = test_id
        self.exercise_number = exercise_number
        self.user_id = user_id
        self.task = Test(test_id).get_task(exercise_number)
        self.answer: Any = self.task.get_empty_answer()

    def set(self, answer):
        self.answer = answer

    def get_score(self):
        a = self.task.score * (self.task.correct_answer == self.answer)
        return a

    @classmethod
    def get_loaded(cls):
        return cls._loaded

    def kill(self):
        self._loaded.pop((self.test_id, self.exercise_number, self.user_id))

    def __repr__(self):
        return f'<<SA task: {self.task} answer: {self.answer}]'

    @property
    def loaded(self):
        return self._loaded


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
@login_required
def personal_account():
    if request.method == 'GET':
        if f'{current_user.get_id()}.png' in os.listdir('static/img'):
            return render_template('personal_account.html', title='YalWeb2022', flag=True,
                                   name=f'static/img/{current_user.get_id()}.png')
        else:
            return render_template('personal_account.html', title='YalWeb2022', flag=False)

    elif request.method == 'POST':
        try:
            sql_gate.update_user(con, current_user.get_id(), new_email=request.form['email'],
                                 new_username=request.form['text'])
            login_manager.needs_refresh()
        except BaseException:
            pass
        try:
            f = request.files['file']
            f.save(f'static/img/{current_user.get_id()}.png')
        except BaseException:
            pass
        return redirect('/personal_account')


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
            return redirect('/login')
    return render_template('signup.html',
                           title='Регистрация',
                           form=form)


def radio_btn(test_id, exercise_number, task_names):
    user_id = current_user.get_id()

    form = TaskInputForm()
    if form.validate_on_submit():
        answer = form.data['answer']
        SavedAnswer(test_id, exercise_number, user_id).set(answer)

    task = Test(test_id).get_task(exercise_number)

    return render_template('multy_choice.html',
                           title='тест',
                           condition=task.text,
                           form=form,
                           task_names=task_names,
                           test_id=test_id)


@app.route('/view_tests', methods=['GET'])
@login_required
def view_tests():
    user_id = current_user.get_id()
    tests = sql_gate.get_tests(con, owner_id=user_id)
    data = []
    for test_id, _, name in tests:
        data.append((test_id, name))
    indexes = []
    len_data = len(data)
    for i in range(0, len_data, 4):
        indexes.append(list())
        for j in range(i, min(i + 4, len_data)):
            indexes[-1].append(j)

    return render_template('view_tests.html',
                           title='мои тесты',
                           data=data,
                           indexes=indexes)


@app.route('/view_test/<int:test_id>', methods=['GET'])
@login_required
def view_test(test_id):
    user_id = current_user.get_id()
    test = sql_gate.get_tests(con, test_id=test_id, owner_id=user_id)

    if not test:
        return redirect('/')

    return redirect('/')  # TODO


@app.route('/pass/<int:test_id>', methods=['GET', 'POST'])
@login_required
def pass_start(test_id):
    if sql_gate.get_results(con, user_id=current_user.get_id(), test_id=test_id):
        return redirect(f'/pass/{test_id}/complete')

    form = PassStartForm()
    if form.validate_on_submit():
        return redirect(f'/pass/{test_id}/1')

    return render_template('pass_start.html',
                           tilte='Начало теста',
                           form=form)


@app.route('/pass/<int:test_id>/<int:exercise_number>', methods=['GET', 'POST'])
@login_required
def pass_handler(test_id, exercise_number):
    if sql_gate.get_results(con, user_id=current_user.get_id(), test_id=test_id):
        return redirect(f'/pass/{test_id}/complete')
    exercise_number -= 1

    if isinstance(Test(test_id).get_task(exercise_number), TaskInput):
        return pass_input(test_id, exercise_number)
    if isinstance(Test(test_id).get_task(exercise_number), TaskChoice):
        return pass_choice(test_id, exercise_number)
    if isinstance(Test(test_id).get_task(exercise_number), TaskMultyChoice):
        return pass_multy_choice(test_id, exercise_number)


def pass_input(test_id, exercise_number):
    task_names = Test(test_id).task_names()
    user_id = current_user.get_id()

    form = TaskInputForm()
    if form.validate_on_submit():
        answer = form.data['answer']
        SavedAnswer(test_id, exercise_number, user_id).set(answer)

    task: TaskInput = Test(test_id).get_task(exercise_number)

    return render_template('pass_input.html',
                           title='тест',

                           task_names=task_names,
                           test_id=test_id,

                           condition=task.text,
                           form=form)


def pass_choice(test_id, exercise_number):
    task_names = Test(test_id).task_names()
    user_id = current_user.get_id()

    task = Test(test_id).get_task(exercise_number)

    form = task.form()
    if form.validate_on_submit():
        SavedAnswer(test_id, exercise_number, user_id).set(form.data['task_choice'])

    checked = SavedAnswer(test_id, exercise_number, user_id).answer
    form.task_choice.default = checked
    return render_template('pass_choice.html',
                           title='тест',

                           task_names=task_names,
                           test_id=test_id,

                           condition=task.text,
                           form=form)


def pass_multy_choice(test_id, exercise_number):
    task_names = Test(test_id).task_names()
    user_id = current_user.get_id()

    task = Test(test_id).get_task(exercise_number)

    form = task.form()
    if form.validate_on_submit():
        a = form.data['task_choice']
        b = SavedAnswer(test_id, exercise_number, user_id)
        b.set(a)
    checked = SavedAnswer(test_id, exercise_number, user_id).answer
    form.task_choice.default = checked
    return render_template('multy_choice.html',
                           title='тест',

                           task_names=task_names,
                           test_id=test_id,

                           condition=task.text,
                           form=form)


@app.route("/pass/<int:test_id>/complete")
@login_required
def pass_complete(test_id):
    user_id = current_user.get_id()
    results = sql_gate.get_results(con, user_id=user_id, test_id=test_id)

    if not results:
        to_kill = []
        max_score = Test(test_id).max_score
        real_score = 0
        for (a_test_id, _, a_user_id), answer in SavedAnswer.get_loaded().items():
            if a_user_id == user_id and a_test_id == test_id:
                real_score += answer.get_score()
                to_kill.append(answer)
        for i in to_kill:
            i.kill()
        sql_gate.add_result(con, user_id, test_id, real_score, max_score)
        results = test_id, user_id, real_score, max_score
    else:
        results = results[-1]
    return render_template('pass_complete.html',
                           title='результаты',

                           score=results[2],
                           max_score=results[3],
                           procentage=f'{results[2] / results[3]:.0%}')


@app.route("/test_creator", methods=['GET', 'POST'])
@login_required
def test_creator():
    form = NewTestForm()
    question = request.args.get('question', default=1, type=int)
    max_question = request.args.get('max_question',
                                    default=(question if question > 10 else 10),
                                    type=int)
    if form.validate_on_submit():
        # Save test
        return redirect('/')
    return render_template("test_creator.html", subjects=SUBJECTS, question=question,
                           max_question=max_question, form=form)


if __name__ == '__main__':
    info('connecting to database...')
    con = sqlite3.connect('db/db.db', check_same_thread=False)
    sql_gate.init_database(con)
    if not os.path.exists('tests_data'):
        os.makedirs('tests_data')
    info('...connected successful')

    app.run()
