import json
from src.ebird.dao import DAO

class User():

    def __init__(self, db_filepath, userid=None):
        self.userid = userid
        self.db = DAO(db_filepath)
        if userid:
            userinfo = self.db.get_user(userid)
            self.username = userinfo.rows[0]
            self.fullname = userinfo.rows[1]
            self.role = userinfo.rows[2]
            self.status = "Verified"
        else:
            self.username = None
            self.fullname = None
            self.role = None
            self.status = "Unverified"

    def getDisplayName(self):
        if self.fullname:
            return self.fullname
        else:
            return self.username

    def authenticate(self, username, password):
        result = self.db.verify_user(username, password)
        if result.status:
            self.username = username
            self.userid = result.rows[0]
            self.fullname = result.rows[1]
            self.role = result.rows[2]
            self.status = "Authenticated '{0}'".format(username)
            return True
        else:
            self.status = result.rows[0]
            return False

    def add(self, username, password, fullname):
        result = self.db.add_user(username, password, fullname)
        if result.status:
            self.status = "New user {0} added".format(result.rowid)
            return result.rowid
        else:
            self.status = "New user failed to add: {0}".format('; '.join(result.rows))
            return 0

    def delete(self, userid):
        result = self.db.delete_user(userid)
        if result.status:
            self.status = "User {0} deleted".format(userid)
            return 1
        else:
            self.status = "User failed to delete"
            return 0

    def getUsers(self):
        result = self.db.list_users()
        if result.status:
            return result.rows
        else:
            return []

    def getResults(self):
        result = self.db.get_results(self.userid)
        if result.status:
            return result.rows
        else:
            return []

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__)