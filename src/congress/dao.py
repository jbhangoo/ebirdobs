from datetime import datetime
import os

from src.db.db import DB
from src.db.db_result import DBResult

db_file_location = "data/congress.db"
root_dir = os.path.join(os.getcwd(), os.pardir, os.pardir)
print(os.path.abspath (root_dir))
VOTE_DB_FILE = os.path.join(root_dir, "data", "congress.db")


# Members of Congress
sql_create_member_table = """
CREATE TABLE IF NOT EXISTS member
	(member_id integer NOT NULL UNIQUE,
	name text NOT NULL UNIQUE
	)
"""

# Instances of Congress: Which members were part of a particular congress
sql_create_congress_table = """
CREATE TABLE IF NOT EXISTS congress
	(id integer PRIMARY KEY,
	congress_number integer NOT NULL,
	member_id integer NOT NULL,
	state text NOT NULL,
	chamber text,
	party text,
	FOREIGN KEY(member_id) REFERENCES member(member_id),
	UNIQUE(congress_number, member_id)
	)
"""
sql_create_rollcall_table = """
CREATE TABLE IF NOT EXISTS rollcall
	(id integer PRIMARY KEY,
	question text,
	description text,
	voted_on timestamp,
	congress_number integer NOT NULL,
	chamber text NOT NULL,
	session integer NOT NULL,
	rollcall_number integer NOT NULL,
	created_on timestamp,
	UNIQUE(congress_number, chamber, session, rollcall_number)
	)
"""

sql_create_vote_table = """
CREATE TABLE IF NOT EXISTS vote
	(id integer PRIMARY KEY,
	member_id integer NOT NULL,
	rollcall_id integer NOT NULL,
	vote integer,
	created_on timestamp,
	FOREIGN KEY(member_id) REFERENCES member(member_id),
	FOREIGN KEY(rollcall_id) REFERENCES rollcall(id)
	)
"""

sql_get_votes = """
select voted_on, congress_number, rollcall_number, name, vote
from rollcall INNER JOIN 
    (vote INNER JOIN member
    on vote.member_id=member.member_id)
on rollcall.id=vote.rollcall_id
ORDER BY voted_on
"""

class DAO():

    def __init__(self, dbfilename):
        self.db =  DB(dbfilename)

        # Set up basic initial database if needed
        r1 = self.db.exec_sql(sql_create_member_table)
        r2 = self.db.exec_sql(sql_create_congress_table)
        r3 = self.db.exec_sql(sql_create_rollcall_table)
        r4 = self.db.exec_sql(sql_create_vote_table)

    def get_member(self, member_id):
        if (not member_id):
            return DBResult(False, ['Invalid member ID'], 0)
        result = self.db.select('member', ['name'], "member_id = '{0}'".format(member_id))
        if (result) and (len(result.rows) == 1) and (len(result.rows[0]) == 1):
                return DBResult(True,result.rows[0])
        else:
            return DBResult(False, ["member ({0}) not found".format(member_id)])

    def add_member(self, member_id, name):
        if (not member_id) or (not name):
            return DBResult(False, ['Invalid member information'], 0)

        return self.db.insert('member', ['member_id', 'name'], [member_id, name])

    def get_congress_member(self, congress_number, member_id):
        if (not congress_number) or (not member_id):
            return DBResult(False, ['Invalid congress member information'], 0)
        result = self.db.select('congress', ['state', 'chamber', 'party'], "(congress_number = {0}) and (member_id = '{0}')".format(member_id))
        if (result) and (len(result.rows) == 1) and (len(result.rows[0]) == 3):
                return DBResult(True,result.rows[0])
        else:
            return DBResult(False, ["congress member ({0}, {1}) not found".format(congress_number, member_id)])

    def add_congress_member(self, congress_number, member_id, state, chamber, party):
        if (not congress_number) or (not member_id):
            return DBResult(False, ['Invalid congress member information'], 0)

        return self.db.insert('congress', ['congress_number', 'member_id', 'state', 'chamber', 'party'],
                              [congress_number, member_id, state, chamber, party])

    def add_rollcall(self, question, description, voted_on, congress_number, chamber, session, rollcall_number):
        timestamp = datetime.timestamp(datetime.now())
        return self.db.insert('rollcall',
              ['question', 'description', 'voted_on', 'congress_number', 'chamber', 'session', 'rollcall_number' ,'created_on'],
              [question, description, voted_on, congress_number, chamber, session, rollcall_number, timestamp])

    def add_vote(self,	member_id, rollcall_id, vote):
        timestamp = datetime.timestamp(datetime.now())
        return self.db.insert('vote', ['member_id', 'rollcall_id', 'vote', 'created_on'], [member_id, rollcall_id, vote, timestamp])

    def get_votes(self):
        return self.db.exec_sql(sql_get_votes)

    def delete_vote(self, result_id):
        return self.db.delete('result', "id={0} ".format(result_id))
