from flask import Flask, redirect, render_template

# from db import sql_gate
from forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    return render_template('index.html', title='YalWeb2022')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    app.run()