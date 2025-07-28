from tinydb import TinyDB
from flask import g


def get_codes_db():
    if "db" not in g:
        g.codes_db = TinyDB("databases/codes_db.json")
    return g.codes_db


def get_attendance_db():
    if "db" not in g:
        g.attendance_db = TinyDB("databases/attendance_db.json")
    return g.attendance_db
