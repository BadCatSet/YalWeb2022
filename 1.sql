PRAGMA foreign_keys = off;
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
