from typing import Iterable

class DBResult():
    def __init__(self, status:bool, rows:Iterable, rowid:int = 0):
        self.status = status
        self.rows = rows
        self.rowid = rowid