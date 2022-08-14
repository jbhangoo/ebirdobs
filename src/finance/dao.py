from datetime import datetime
import yfinance as yahooFinance

from src.db.db import DB
from src.db.db_result import DBResult

db_file_location = "data/finance.db"

sql_create_benchmark_table = """
CREATE TABLE IF NOT EXISTS benchmark
	(id integer PRIMARY KEY,
	symbol text NOT NULL UNIQUE,
	name text NOT NULL UNIQUE,
	description text NOT NULL UNIQUE
	)
"""

sql_create_trade_table = """
CREATE TABLE IF NOT EXISTS trade
	(id integer PRIMARY KEY,
	benchmark_id integer NOT NULL,
	trade_date date NOT NULL,
	closing_price double precision,
	created_on timestamp,
	FOREIGN KEY(benchmark_id) REFERENCES benchmark(id)
	)
"""

class DAO():

    def __init__(self, dbfilename):
        self.db =  DB(dbfilename)

        # Set up basic initial database if needed
        self.db.exec_sql(sql_create_benchmark_table)
        self.db.exec_sql(sql_create_trade_table)

    def load_benchmarks(self, benchmarks):
        '''
        Put contents of benchmarks (list of lists) into database table
        :param benchmark:
        :return:
        '''
        benchmark_ids = {}
        self.benchmarks = {}
        for benchmark_data in benchmarks:
            symbol = benchmark_data[2]
            result_id = self.get_benchmark_id(symbol)
            if result_id:
                self.benchmarks[result_id] = symbol
                benchmark_ids[symbol] = result_id
            else:
                result = self.db.insert("benchmark", ['name', 'description', 'symbol'], benchmark_data)
                if result.status:
                    benchmark_ids[symbol] = result.rows[0][0]
        return benchmark_ids

    def list_benchmarks(self):
        '''
        Return all benchmarks in the DB
        :return:
        '''
        results = self.db.select('benchmark', ['id', 'symbol', 'name', 'description'])
        if results.status:
            return results.rows
        else:
            return []

    def get_benchmark_id(self, symbol):
        '''
        Return the primary key of the given symbol in the benchmark table
        :param symbol:
        :return:
        '''
        results =  self.db.select('benchmark', ['id'], "symbol='{}'".format(symbol))
        if results.status:
            return results.rows[0][0]
        else:
            return None

    def get_last_trade_date(self, benchmark):
        sql = "select max(trade_date) from trade inner join benchmark on trade.benchmark_id=benchmark.id "
        sql += "where benchmark.symbol='{}'".format(benchmark)
        last_trade = self.db.exec_sql(sql)
        if last_trade.status:
            last_date = last_trade.rows[0]
            return last_date
        else:
            return None

    def load_prices(self, benchmark, from_date=None):
        '''
        Load database with trade closing prices from Yahoo Finance
        from given date to today
        :param from_date: If None, fill all missing dates between last trade date in the DB table
        :return:
        '''
        if from_date is None:
            from_date = self.get_last_trade_date(benchmark)
            if not from_date:
                from_date = "2022-08-01"
        today = datetime.today()
        prices = self.get_yahoo_prices(benchmark, from_date, today)
        benchmark_id = self.get_benchmark_id(benchmark)
        if benchmark_id:
            return self.add_trades(benchmark_id, prices)
        else:
            return None

    def add_trades(self, benchmark_id, prices):
        for d, p in zip(prices.index, prices.values):
            result = self.add_trade(benchmark_id, d, p)
            if not result.status:
                return []
        return prices

    def get_yahoo_prices(self, symbol, startDate, endDate):
        '''
        Request daily closing prices for given symbol between given dates
        :param symbol:      Ticker symbol
        :param startDate:
        :param endDate:
        :return:    Pandas Series of price values indexed by date
        '''
        asset = yahooFinance.Ticker(symbol)
        historical = asset.history(start=startDate, end=endDate, interval='1d')
        # get Pandas Series of daily closing prices over date range
        prices = historical.Close
        return prices

    def get_prices(self, benchmark_id, start_date, end_date=None):
        '''
        Query DB and return daily closing prices for given benchmark between given dates
        :param benchmark_id:    Primary key of benchmark to get prices for
        :param start_date:
        :param end_date:
        :return:
        '''
        if (not benchmark_id):
            return DBResult(False, ['Invalid benchmark ID'], 0)
        if not end_date:
            end_date = datetime.today().strftime("%Y-%m-%d")
        result = self.db.select('trade', ['trade_date', 'closing_price'],
                "(benchmark_id = {}) and (trade_date between '{}' and '{}')".format(benchmark_id, start_date, end_date))
        if (result) and (len(result.rows) == 1) and (len(result.rows[0]) == 3):
                return DBResult(True,result.rows)
        else:
            # No data. Fill from Yahoo Finance
            benchmark = self.benchmarks[benchmark_id]
            prices = self.get_yahoo_prices(benchmark, start_date, end_date)
            results = self.add_trades(benchmark_id, prices)
            if len(results) > 0:
                return DBResult(True,prices)
            return DBResult(False, ["Insert trades to DB failure"], 0)

    def add_benchmark(self, symbol, name, description):
        if not symbol:
            return DBResult(False, ['Invalid symbol'], 0)
        return self.db.insert('benchmark', ['symbol', 'name', 'description'], [symbol, name, description])

    def add_trade(self, benchmark_id, trade_date, closing_price):
        if (not benchmark_id) or (not trade_date) or (not closing_price):
            return DBResult(False, ['Invalid trade information'], 0)
        timestamp = str(datetime.timestamp(datetime.now()))
        if not isinstance(trade_date, str):
            trade_date = trade_date.strftime("%Y-%m-%d")
        return self.db.insert('trade', ['benchmark_id', 'trade_date', 'closing_price', 'created_on'],
                              [ benchmark_id, trade_date, closing_price, timestamp])

    def delete_trade(self, trade_id):
        return self.db.delete('trade', "id={0} ".format(trade_id))
