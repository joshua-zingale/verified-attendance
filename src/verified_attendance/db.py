from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from flask import g


def get_codes_db(in_memory=False):
    if "db" not in g:
        g.codes_db = TinyDB(storage=MemoryStorage) if in_memory else TinyDB("databases/codes_db.json")
    return g.codes_db


def get_attendance_db(in_memory=False):
    if "db" not in g:
        g.attendance_db = TinyDB(storage=MemoryStorage) if in_memory else TinyDB("databases/attendance_db.json")
    return g.attendance_db
