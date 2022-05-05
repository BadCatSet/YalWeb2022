from hashlib import sha256
from sqlite3.dbapi2 import Connection as Con

from typing import Any, List


def hasher(a: str):
    return sha256(bytes(a, 'utf-8')).hexdigest()


def nn(a):
    return a is not None


def construct_select(con: Con, base_table: str, fields: List[str] = None, where: dict = None):
    if fields is None:
        fields = ['*']
    if where is None:
        where = {}

    call = f"""SELECT {', '.join(fields)} FROM {base_table} WHERE"""

    where_exists = False
    args = []
    for n, (arg, val) in enumerate(where.items()):
        if nn(val):
            where_exists = True
            call += f""" {arg}=? and"""
            args.append(val)
    return con.execute(call[:(-4 if where_exists else -6)], args)


def construct_insert(con: Con, base_table: str, values: dict[str, Any] = None):
    cur = con.cursor()
    fields = list()
    args = list()
    for k, v in values.items():
        if nn(v):
            fields.append(k)
            args.append(v)

    call = f"""INSERT INTO {base_table} ({', '.join(fields)}) VALUES ({', '.join('?' * len(args))})"""

    cur.execute(call, args)
    con.commit()
    return cur.lastrowid


def construct_update(con: Con, base_table: str, fields: dict, where: dict):
    args = list()
    call = f"""UPDATE {base_table} SET """
    call += ', '.join([(f"""{k} = ?""", args.append(v))[0] for k, v in fields.items() if nn(v)])
    call += """ WHERE """
    call += ', '.join([(f"""{k} = ?""", args.append(v))[0] for k, v in where.items() if nn(v)])
    cur = con.cursor()
    cur.execute(call, args)
    con.commit()
    return cur.lastrowid


def get_tests(con: Con, test_id=None, owner_id=None):
    """
    :param con: Connection
    :param test_id: id
    :param owner_id: owner_id
    :return: test by args
    """
    attrs = {'id': test_id, 'owner_id': owner_id}
    return construct_select(con, 'tests', where=attrs).fetchall()


def get_users(con: Con, user_id=None, email=None, password: str = None):
    """
    :param con: Connection
    :param user_id: user_id
    :param email: email
    :param password: password(not hashed)
    :return: users by args
    """
    attrs = {'id': user_id,
             'email': email,
             'password_h': hasher(password) if nn(password) else None}
    return construct_select(con, 'users', where=attrs).fetchall()


def get_results(con: Con, user_id=None, test_id=None):
    """
    :param con: Connection
    :param user_id: user_id
    :param test_id: test_id
    :return: results by args
    """
    attrs = {'user_id': user_id,
             'test_id': test_id}
    return construct_select(con, 'results', where=attrs).fetchall()


def add_user(con: Con, email: str, password: str, username: str = None):
    attrs = {
        'email': email,
        'password_h': hasher(password),
        'username': username
    }
    return construct_insert(con, 'users', attrs)


def add_result(con: Con, user_id, test_id, real_score, max_score):
    attrs = {
        'user_id': user_id,
        'test_id': test_id,
        'real_score': real_score,
        'max_score': max_score
    }
    return construct_insert(con, 'results', attrs)


def add_test(con: Con, test_id=None, owner_id=None):
    attrs = {
        'test_id': test_id,
        'owner_id': owner_id
    }
    return construct_insert(con, 'tests', attrs)


def update_user(con: Con, user_id, new_email=None, new_username=None):
    attrs = {'email': new_email,
             'username': new_username}
    return construct_update(con, 'users', attrs, {'id': user_id})


def init_database(con: Con):
    s = """PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

CREATE TABLE if not exists results (
    test_id    INTEGER REFERENCES tests (id) 
                       NOT NULL,
    user_id    INTEGER REFERENCES users (id) 
                       NOT NULL,
    real_score DOUBLE  NOT NULL,
    max_score  INTEGER NOT NULL
);




CREATE TABLE if not exists tests (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     NOT NULL
                     DEFAULT (1),
    owner_id INTEGER NOT NULL
                     REFERENCES users (id),
    name     STRING
);



CREATE TABLE if not exists users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT
                       UNIQUE
                       NOT NULL,
    email      STRING  UNIQUE
                       NOT NULL,
    password_h STRING  NOT NULL,
    username   STRING  UNIQUE
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
"""
    for i in s.split(';'):
        con.execute(i)
    con.commit()
