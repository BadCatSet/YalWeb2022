from hashlib import sha256
from sqlite3.dbapi2 import Connection as Con


def hasher(a: str):
    return sha256(bytes(a, 'utf-8')).hexdigest()


def nn(a):
    return a is not None


def complex_select(con: Con, base_table: str, fields: list[str] | None = None, where: dict | None = None):
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


def construct_insert(con, base_table: str, values: dict | None = None):
    pass


def get_test(con: Con, test_id=None, owner_id=None):
    """
    :param con: Connection
    :param test_id: id
    :param owner_id: owner_id
    :return: test by args
    """
    attrs = {'id': test_id, 'owner_id': owner_id}
    return complex_select(con, 'tests', where=attrs).fetchall()


def get_users(con: Con, user_id=None, email=None, password: str | None = None):
    """
    :param con: Connection
    :param user_id: id
    :param email: email
    :param password: password(not hashed)
    :return: users by args
    """
    attrs = {'id': user_id,
             'email': email,
             'password_h': hasher(password) if nn(password) else None}
    return complex_select(con, 'users', where=attrs).fetchall()


def add_user(con: Con, email: str, password: str, username: str | None = None):
    con.execute(f"""INSERT INTO users(email, password_h) VALUES(?, ?)""", (email, hasher(password)))
    con.commit()
