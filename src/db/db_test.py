import os
from src.ebird.dao import DAO

dbfilename = os.path.join(os.getcwd(), "../..", "data", "ebirdobs.db")

database = DAO(dbfilename)
valid = database.verify_user("test", "test")

print(valid.status)
for row in valid.rows:
    print(row)
