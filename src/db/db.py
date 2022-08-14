import sqlite3
from src.db.db_result import DBResult

class DB():
    def __init__(self, db_file:str):
        """
        Connect to a SQLite database
        :param db_file: path to SQite DB file
        :return:        connection handle to DB
        """
        self.dbfile = db_file

    def exec_sql(self, sql:str, args:list = None):
        """
        Execute sql command and return raw response
        :param sql:
        :return: All rows returned by the sql query
        """
        try:
            with sqlite3.connect(self.dbfile) as conn:
                cur = conn.cursor()
                if args:
                    result = cur.execute(sql, args)
                else:
                    result = cur.execute(sql)
                rowid = cur.lastrowid
                rows = []
                for row in result:
                    rows.append(row)
                cur.close()
                return DBResult(True, rows, rowid)
        except sqlite3.Error as sqlError:
            return DBResult(False, [str(sqlError)])
        except Exception as error:
            return DBResult(False, [str(error)])

    def select(self, table:str, columns:list, criteria:str=None):
        """
        Select all rows from given table and columns, according to criteria
        :param table:       table to query
        :param columns:     Return these columns
        :param criteria:    Properly formatted SQL WHERE clause
        :return:            list of tuples for query result
        """

        sql = "SELECT {} FROM {}".format(','.join(columns), table)
        if criteria:
            sql += " WHERE {}".format(criteria)
        result = self.exec_sql(sql)
        return result

    def insert(self, table:str, columns: list, values: list):
        """
        Format and issue SQL INSERT using given values
        :param table:       name of table to insert values into
        :param columns:     iterable of column names to insert
        :param values:      tuple of actual values to insert
        :return:            ID of new row created
        """
        args = ['?' for c in columns]
        sql = "INSERT INTO {}({}) VALUES ({})".format(table, ','.join(columns), ','.join(args))
        return self.exec_sql(sql, values)

    def delete(self, table:str, criteria:str):
        """
        Format and issue SQL DELETE using given values
        :param table:       name of table to delete values from
        :param criteria:    SQL criteria identifying which rows to delete
        :return:            number of rows deleted
        """
        sql = "DELETE FROM {} WHERE {}".format(table, criteria)
        return self.exec_sql(sql)
