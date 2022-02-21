from hashlib import sha256 as hasher
from sqlite3.dbapi2 import Connection as Con


def nn(a):
    return a is not None


def construct(args: dict):
    exists = list(map(nn, args.values()))
    if not any(exists):
        return """"""
    call = """ WHERE"""
    attrs = []
    for n, (arg, val) in enumerate(args.items()):
        if exists[n]:
            call += f""" {arg}=? and"""
            attrs.append(val)
    return call[:-4], attrs


def get_exercise(con: Con, self_id=None, owner_id=None):
    """
    :param con: Connection
    :param self_id: id
    :param owner_id: owner_id
    :return: exercises by args
    """
    attrs = {'id': self_id, 'owner_id': owner_id}
    return con.execute(*construct(attrs)).fetchall()


def get_users(con: Con, self_id=None, email=None, password: str | None = None):
    """
    :param con: Connection
    :param self_id: id
    :param email: email
    :param password: password(not hashed)
    :return: users by args
    """
    attrs = {
        'id': self_id,
        'email': email,
        'password': hasher(password) if nn(password) else None}
    return con.execute(*construct(attrs)).fetchall()
