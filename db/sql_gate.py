from hashlib import sha256
from sqlite3.dbapi2 import Connection as Con


def hasher(a: str):
    return sha256(bytes(a, 'utf-8')).hexdigest()


def nn(a):
    return a is not None


def construct(prefix: str, args: dict):
    exists = list(map(nn, args.values()))
    if not any(exists):
        return prefix
    call = prefix + """ WHERE"""
    attrs = []
    for n, (arg, val) in enumerate(args.items()):
        if exists[n]:
            call += f""" {arg}=? and"""
            attrs.append(val)
    return call[:-4], attrs


def get_exercise(con: Con, _id=None, owner_id=None):
    """
    :param con: Connection
    :param _id: id
    :param owner_id: owner_id
    :return: exercises by args
    """
    attrs = {'id': _id, 'owner_id': owner_id}
    call = construct("""SELECT * FROM exercises""", attrs)
    return con.execute(*call).fetchall()


def get_users(con: Con, _id=None, email=None, password: str | None = None):
    """
    :param con: Connection
    :param _id: id
    :param email: email
    :param password: password(not hashed)
    :return: users by args
    """
    attrs = {'id': _id, 'email': email, 'password_h': hasher(password) if nn(password) else None}
    call = construct("""SELECT * FROM users""", attrs)
    return con.execute(*call).fetchall()


def add_user(con: Con, email: str, password: str):
    con.execute(f"""INSERT INTO users(email, password_h) VALUES(?, ?)""", (email, hasher(password)))
    con.commit()
