from datetime import datetime

import numpy as np
import pandas as pd
import yfinance
from typing import List

from src.finance.ticker import Ticker
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

sql_drop_trade_table = "DROP TABLE IF EXISTS trade"
sql_create_trade_table = """
CREATE TABLE IF NOT EXISTS trade
	(id integer PRIMARY KEY,
	benchmark_id integer NOT NULL,
	trade_date date NOT NULL,
	closing_price double precision,
	high_price double precision,
	low_price double precision,
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

    def insert_ticker(self, ticker:Ticker):
        '''
        First, check if ticker is already in the database. If so, return its primary key
        Otherwise, insert it into the database then return the new primary key created
        :param ticker:  Ticker object of asset
        :return:        Primary key of ticker's symbol
        '''
        result_id = self.get_benchmark_id(ticker.symbol)
        if result_id:
            return result_id
        else:
            results = self.db.insert("benchmark", ['name', 'description', 'symbol'], [ticker.definition, ticker.description, ticker.symbol])
            if results.status and (len(results.rows) > 0) and (len(results.rows[0]) > 0):
                return results.rowid
            else:
                return None

    def load_benchmarks(self, benchmarks: List[Ticker]):
        '''
        Put contents of benchmarks (list of lists) into database table
        :param benchmark:
        :return:
        '''
        benchmark_ids = {}
        self.benchmarks = {}
        for benchmark in benchmarks:
            symbol = benchmark.symbol
            result_id = self.get_benchmark_id(symbol)
            if result_id:
                self.benchmarks[result_id] = symbol
                benchmark_ids[symbol] = result_id
            else:
                result = self.db.insert("benchmark", ['name', 'description', 'symbol'],
                                        [benchmark.description, benchmark.description, symbol])
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
        if results.status and (len(results.rows) > 0) and (len(results.rows[0]) > 0):
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
        prices, highs, lows = self.get_yahoo_prices(benchmark, from_date, today)
        benchmark_id = self.get_benchmark_id(benchmark)
        if benchmark_id:
            return self.add_trades(benchmark_id, prices, highs, lows)
        else:
            return None

    def get_prices(self, benchmark_id:int, symbol:str, start_date, end_date=None)->dict:
        '''
        Query DB and return daily closing prices for given benchmark between given dates
        :param benchmark_id:    Primary key of benchmark to get prices for
        :param symbol:          benchmark symbol if needed to get prices from Yahoo Finance
        :param start_date:
        :param end_date:
        :return: Pandas dataframe of prices for each trading day (session) between the given dates
        '''
        if (not benchmark_id):
            return {'error': 'Invalid benchmark ID'}
        if not end_date:
            end_date = datetime.today().strftime("%Y-%m-%d")
        result = self.db.select('trade', ['trade_date', 'closing_price', 'high_price', 'low_price'],
                "(benchmark_id = {}) and (trade_date between '{}' and '{}')".format(benchmark_id, start_date, end_date),
                                order='trade_date')
        if result and result.status and (len(result.rows) > 0):
            priceArr = np.transpose(result.rows)
            prices = {
                'tradedate':    priceArr[0],
                'closing':      [float(x) for x in priceArr[1]],
                'high':         [float(x) for x in priceArr[2]],
                'low':          [float(x) for x in priceArr[3]],
            }
            return prices
        else:
            # No data. Fill from Yahoo Finance
            dates, closings, highs, lows = self.get_yahoo_prices(symbol, start_date, end_date)
            ids = self.add_trades(benchmark_id, dates, closings, highs, lows)
            if len(ids) > 0:
                prices = {
                    'tradedate': dates,
                    'closing': closings,
                    'high': highs,
                    'low': lows
                }
                return prices
            return {'error': 'Failed to add trades to database'}


    def get_yahoo_prices(self, symbol, startDate, endDate):
        '''
        Request daily closing prices for given symbol between given dates
        :param symbol:      Ticker symbol
        :param startDate:
        :param endDate:
        :return:    Pandas Series of price values indexed by date
        '''
        asset = yfinance.Ticker(symbol)
        historical = asset.history(start=startDate, end=endDate, interval='1d')
        # get Pandas Series of daily closing prices over date range
        dates = historical.Close.index
        closes = historical.Close.values
        highs = historical.High.values
        lows = historical.Low.values
        return (dates, closes, highs, lows)

    def add_benchmark(self, symbol, name, description):
        if not symbol:
            return DBResult(False, ['Invalid symbol'], 0)
        return self.db.insert('benchmark', ['symbol', 'name', 'description'], [symbol, name, description])

    def add_trades(self, benchmark_id, dates, closes, highs, lows):
        ids = []
        for i in range(len(dates)):
            result = self.add_trade(benchmark_id,  dates[i], closes[i], highs[i], lows[i])
            if not result.status:
                ids.append(None)
            else:
                ids.append(result.rowid)
        return ids

    def add_tradesOLD(self, benchmark_id, dates, closes, highs, lows):
        dates = []
        for i in range(len(closes)):
            dt = closes.index[i]
            dates.append(dt)
            close = closes.values[i]
            high = highs.values[i]
            low = lows.values[i]
            result = self.add_trade(benchmark_id, dt, close, high, low)
            if not result.status:
                return []
        return dates

    def add_trade(self, benchmark_id:int, trade_date, closing_price:float, high_price:float, low_price:float):
        if (not benchmark_id) or (not trade_date) or (not closing_price):
            return DBResult(False, ['Invalid trade information'], 0)
        timestamp = str(datetime.timestamp(datetime.now()))
        if not isinstance(trade_date, str):
            trade_date = trade_date.strftime("%Y-%m-%d")
        return self.db.insert('trade', ['benchmark_id', 'trade_date', 'closing_price', 'high_price', 'low_price', 'created_on'],
                              [ benchmark_id, trade_date, closing_price, high_price, low_price, timestamp])

    def delete_trade(self, trade_id):
        return self.db.delete('trade', "id={0} ".format(trade_id))
