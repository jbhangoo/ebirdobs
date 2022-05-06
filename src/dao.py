import hashlib
from datetime import datetime

from src.db import DB
from src.db_result import DBResult

db_file_location = "data/transvax.db"

sql_create_role_table = """
CREATE TABLE IF NOT EXISTS role
	(id integer PRIMARY KEY,
	rolename text NOT NULL UNIQUE
	)
"""

sql_create_user_table = """
CREATE TABLE IF NOT EXISTS user
	(id integer PRIMARY KEY,
	username text NOT NULL UNIQUE,
	pw text NOT NULL,
	fullname text,
	key double precision,
	role_id integer,
	created_on timestamp,
	FOREIGN KEY(role_id) REFERENCES role(id)
	)
"""

sql_create_results_table = """
CREATE TABLE IF NOT EXISTS result
	(id integer PRIMARY KEY,
	birth_rate_file text,
	result_directory text unique,
	simulated_on timestamp,
	user_id integer,
	FOREIGN KEY(user_id) REFERENCES user(id)
	)
"""

class DAO():

    def __init__(self, dbfilename):
        self.db =  DB(dbfilename)

        # Set up basic initial database if needed
        self.db.exec_sql(sql_create_role_table)
        self.db.exec_sql(sql_create_user_table)
        self.db.exec_sql(sql_create_results_table)
        allusers = self.list_users()
        if not allusers.rows:
            self.add_role("user")
            self.add_role("superuser")
            self.add_user("guest", "G5", "Guest", 0)
            self.add_user("admin", "F4", "Admin", 1)

    def list_users(self):
        return self.db.select('user', ['id', 'username', 'fullname', 'role_id'])

    def verify_user(self, username, raw_pw):
        if (not username) or (not raw_pw):
            return DBResult(False, ['Invalid user information'], 0)
        result = self.db.select('user', ['id', 'pw', 'fullname', 'role_id'], "username = '{0}'".format(username))
        if (result) and (len(result.rows) == 1) and (len(result.rows[0]) == 4):
            pw = hashlib.sha256(raw_pw.encode()).hexdigest()
            if result.rows[0][1] == pw:
                return DBResult(True, [ result.rows[0][0], result.rows[0][2], result.rows[0][3] ])
            else:
                return DBResult(False, ["Authentication failed"])
        return DBResult(False, ["Login attempt failed"])

    def get_user(self, userid):
        if (not userid):
            return DBResult(False, ['Invalid user ID'], 0)
        result = self.db.select('user', ['username', 'fullname', 'role_id'], "id = '{0}'".format(userid))
        if (result) and (len(result.rows) == 1) and (len(result.rows[0]) == 3):
                return DBResult(True,result.rows[0])
        else:
            return DBResult(False, ["User ({0}) not found".format(userid)])

    def delete_user(self, id:int):
        '''
        Delete user with given primary key
        :param id:
        :return:
        '''
        result = self.db.delete('user', 'id={0}'.format(id))
        if result.status:
            # when we delete a user from database USERS, we also need to delete all his or her  data from grid
            result = self.db.delete('grid', 'user_id={0}'.format(id))
        return result

    def add_role(self, rolename):
        if not rolename:
            return DBResult(False, ['Invalid role information'], 0)
        return self.db.insert('role', ['rolename'], [rolename])

    def add_user(self, username, raw_pw, fullname, role_id=None):
        if (not username) or (not raw_pw):
            return DBResult(False, ['Invalid user information'], 0)
        timestamp = datetime.timestamp(datetime.now())
        pw = hashlib.sha256(raw_pw.encode()).hexdigest()
        return self.db.insert('user', ['username', 'pw', 'fullname', 'role_id', 'created_on'],
                              [username, pw, fullname, role_id, timestamp])

    def get_results(self, user_id, simulation_date=None):
        criteria = "user_id={0}".format(user_id)
        if simulation_date:
            criteria += " AND simulated_on='{0}'".format(simulation_date)
        criteria += " ORDER BY simulated_on DESC LIMIT 20"
        return self.db.select('result', ['id', 'simulated_on', 'result_directory'], criteria)

    def add_result(self, user_id, result_directory):
        columns = ['user_id', 'result_directory', 'simulated_on']
        sim_datetime = datetime.timestamp(datetime.now())
        return self.db.insert('result', columns, [user_id, result_directory, sim_datetime])

    def delete_result(self, result_id):
        return self.db.delete('result', "id={0} ".format(result_id))
