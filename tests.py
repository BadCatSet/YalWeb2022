import sqlite3


from db import sql_gate


def test_db1():
    assert sql_gate.get_users(con, user_id=0) == [
        (0, 'pytest', '2b01214d32c382dbc73bf6b493bedb7926324af27bad3ee888f66774b9b114c8', 'pytest username')]


def test_db2():
    assert sql_gate.get_users(con, email='pytest') == [
        (0, 'pytest', '2b01214d32c382dbc73bf6b493bedb7926324af27bad3ee888f66774b9b114c8', 'pytest username')]


def test_db3():
    assert sql_gate.get_users(con, password='pytest') == [
        (0, 'pytest', '2b01214d32c382dbc73bf6b493bedb7926324af27bad3ee888f66774b9b114c8', 'pytest username')]


con = sqlite3.connect('db/db.db')
test_db1()
