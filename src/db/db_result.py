
class DBResult():
    def __init__(self, status:bool, rows:list, rowid:int = 0):
        self.status = status
        self.rows = rows
        self.rowid = rowid