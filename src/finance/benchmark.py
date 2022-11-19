import datetime
import json
import numpy as np
import os
import pandas as pd
import plotly
from pprint import pprint
from scipy.signal import argrelextrema
import statistics
from typing import Iterable
from src.finance.dao import DAO
from src.finance.ticker import load_ticker_file, Ticker

TICKERFILE = os.path.join(os.path.curdir, "data", "tickers.json")
DBFILE =  os.path.join(os.path.curdir, "data", "finance.db")

class Benchmark(object):
    def __init__(self):
        self.benchmarks = load_ticker_file(TICKERFILE)
        self.db = DAO(DBFILE)
        self.benchmark_ids = {}
        for benchmark in self.benchmarks:
            id = self.db.get_benchmark_id(benchmark)
            if id is None:
                id = self.db.insert_ticker(benchmark)
            if id:
                self.benchmark_ids[benchmark.symbol] = id

    def get_prices_recent(self, benchmark)->dict:
        benchmark_id = self.benchmark_ids[benchmark]
        if benchmark_id:
            today = datetime.datetime.today()
            testdate = datetime.date(2020, 10, 29)

            firstday = datetime.date(2016, 1, 1)
            lastday = datetime.date(2022, 11, 11)
            yeatsago = firstday + datetime.timedelta(days=-450)

            prices = self.db.get_prices(benchmark_id, benchmark, testdate, today)
            #prices = self.db.get_prices(benchmark_id, benchmark, firstday, lastday)
            #prices = self.db.get_prices(benchmark_id, benchmark, lastday, today)
            return prices
        else:
            return {'error': 'benchmark {} not supported'.format(benchmark)}

    def get_charts(self):
        charts = []
        for benchmark in self.benchmarks:
            symbol = benchmark.symbol
            prices = self.get_prices_recent(symbol)
            traces = self.create_traces(benchmark, prices)
            charts.append(traces)
        graphJSON = json.dumps(charts, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

    def create_traces(self, benchmark:Ticker, prices:dict):
        smoothed = self.smoothed(prices['closing'], 4)
        extrema = self.local_peaks(smoothed, 4)
        moving_avgs = self.moving_averages(prices['closing'], [10, 50, 200])
        resistance_support = self.resistance_support(prices, smoothed)
        buy_sell = self.buy_sell_points(smoothed, 5)
        bull_bear_points = self.bull_bear_crossover(moving_avgs, 50, 200)
        data = dict(
            x=prices['tradedate'],
            y=prices['closing'],
            smoothed=smoothed,
            support=resistance_support['support'],
            resistance=resistance_support['resistance'],
            avg50=moving_avgs[50],
            avg200=moving_avgs[200],
            bull=bull_bear_points[0],
            bear=bull_bear_points[1],
            #buy=buy_sell[0],
            #sell=buy_sell[1],
            #lows=extrema[0],
            #highs=extrema[1],
            name=benchmark.definition,
            desc=benchmark.description
        )
        return data

    def indexes_to_array(self, min_idxs, prices):
        mins = [None] * len(prices)
        for i in range(len(min_idxs)):
            min_idx = min_idxs[i]
            if prices[min_idx] > 1:
                mins[min_idx] = prices[min_idx]
        return mins

    def resistance_support(self, prices:dict, avg:Iterable):
        """
        Pivot point (PP) = (High + Low +Close)/3
        First resistance (R1) = (2xxPP)-Low
        First support (S1) = (2xPP)-High
        Second resistance (R2) = PP + (High – Low)
        Second support (S2) = PP – (High – Low)
        Third resistance (R3) = High + 2 x (PP - Low)
        Third support (S3) = Low - 2 x (High - PP)
        Source: https://www.fxcc.com/supportresistance-levels-and-pivot-points-lesson-3#
        """
        df_prices = pd.DataFrame(prices, columns=['tradedate', 'closing', 'high', 'low'])
        df_prices['pivot'] = df_prices[['closing', 'high', 'low']].mean(numeric_only=True, axis=1)

        df_prices['r1'] = 2*df_prices['pivot'] - df_prices['low']
        df_prices['resistance1'] = df_prices['r1'].shift(1)
        df_prices['s1'] = 2*df_prices['pivot'] - df_prices['high']
        df_prices['support1'] = df_prices['s1'].shift(1)

        df_prices['resistance2'] = df_prices['pivot'] - df_prices['low'] + df_prices['high']
        df_prices['support2'] = df_prices['pivot'] - df_prices['high'] + df_prices['low']
        df_prices['resistance3'] = df_prices['high'] + 2*(df_prices['pivot'] - df_prices['low'])
        df_prices['support3'] = df_prices['low'] - 2*(df_prices['high'] - df_prices['pivot'])

        df_prices['avg']  = avg
        df_prices['resistance'] = np.where(df_prices['avg'] > df_prices['resistance3'], df_prices['closing'], None)
        df_prices['support'] = np.where(df_prices['avg'] < df_prices['support3'], df_prices['closing'], None)
        return df_prices

    def moving_averages(self, prices, periods) -> dict:
        moving_avgs = {}
        for days in periods:
            moving_avg = [None] * len(prices)
            for i in range(len(prices) - days):
                moving_avg[i + days] = statistics.mean(prices[i:i + days])
            moving_avgs[days] = moving_avg
        return moving_avgs

    def smoothed(self, prices, factor) -> list:
        '''
        Averaged to smooth out minor variations to show sustained trends.
        Local peaks are identified after smoothing
        :param prices:
        :param factor: 1/2 the window size, minus 1
        :return:
        '''
        smooth_line = [None] * len(prices)
        for i in range(factor, len(prices) - factor):
            smooth_line[i] = statistics.mean(prices[i - factor:i + factor])
        return smooth_line

    def bull_bear_crossover(self, moving_avgs:dict, short_term:int, long_term:int):
        '''
        Identify prices where moving average differential indicates where bull
        market crosses over to bear market and vice versa
        :param moving_avgs: dict of moving averages. Must contain keys: short and long
        :param short_term:  number of days in the short term average
        :param long_term:   number of days in the long term average
        :return:            Pair of lists (bull_prices,bear_prices)
        '''
        short_trend = moving_avgs[short_term]
        long_trend = moving_avgs[long_term]

        crossover_buy = [None] * len(short_trend)
        crossover_sell = [None] * len(short_trend)
        for i in range(len(short_trend)-1):
            if short_trend[i] and short_trend[i + 1] and long_trend[i] and long_trend[i + 1]:
                if (short_trend[i] < long_trend[i]) and (short_trend[i+1] > long_trend[i+1]):
                    crossover_buy[i+1] = long_trend[i+1]
                elif (short_trend[i] > long_trend[i]) and (short_trend[i+1] < long_trend[i+1]):
                    crossover_sell[i+1] = long_trend[i+1]
        return (crossover_buy,crossover_sell)

    def local_peaks(self, price_list:list, window=5, tolerance=1):
        '''
        Find theoretical buy and sell points based on extrema within
        a neighborhood of the given prices list
        :param prices:  list of prices, should be averaged/smoothed
        :param window:  radius of local neighborhood
        :param tolerance:   tolerance as percentange of price. Consecutive peaks are
                            considered similar if they are within this tolerance
        :return:        pair of price lists, showing min and max pts resp.
        '''
        # Find local peaks
        prices = np.array([0 if x is None else x for x in price_list])
        min_idxs = argrelextrema(prices, np.less_equal, order=window)
        mins = self.indexes_to_array(min_idxs[0], prices)

        max_idxs = argrelextrema(prices, np.greater_equal, order=window)
        maxs = self.indexes_to_array(max_idxs[0], prices)

        """ maxs = [None] * len(prices)
        for i in range(len(max_idxs[0])):
            max_idx = max_idxs[0][i]
            if prices[max_idx] > 1:
                maxs[max_idx] = prices[max_idx]"""

        return mins, maxs

    def buy_sell_points(self, price_list:list, window=5, tolerance=0.15):
        '''
        Find theoretical buy and sell points based on extrema within
        a neighborhood of the given prices list
        :param prices:  list of prices, should be averaged/smoothed
        :param window:  radius of local neighborhood
        :param tolerance:   tolerance as percentange of price. Consecutive peaks are
                            considered similar if they are within this tolerance
        :return:        pair of price lists, showing min and max pts resp.
        '''
        # Find local peaks
        prices = np.array([0 if x is None else x for x in price_list])
        allmin_idxs = argrelextrema(prices, np.less_equal, order=window)[0]
        max_idxs = argrelextrema(prices, np.greater_equal, order=window)[0]
        # Clip off values outside the window
        min_idxs = allmin_idxs[window-2:-window+2]
        min_flag = min_idxs[0] < max_idxs[0]

        pprint(min_idxs)
        pprint(len(min_idxs))
        pprint(max_idxs)
        pprint(len(max_idxs))

        # Check for buy signals
        double_bottom = []
        for i in range(len(min_idxs) - 1):
            price1 = prices[min_idxs[i]]
            price2 = prices[min_idxs[i+1]]
            if abs(price1 - price2) < (tolerance * price1):
                # Find the max price swing between the two peaks (crest)
                crest_offset = 1
                if min_flag:
                    crest_offset = 0
                if (i+crest_offset) < len(max_idxs):
                    crest = price_list[max_idxs[i+crest_offset]]
                    diff = crest - price1
                    target_price = price2 + diff

                    # Verify the price gained more than the "crest" before the next max pt
                    if (i+crest_offset+1) < len(max_idxs):
                        next_max_idx = max_idxs[i+crest_offset+1]
                        if price_list[next_max_idx] > target_price:
                            double_bottom.append(i+1)

        double_top = []
        buys = self.indexes_to_array(double_bottom, prices)
        sells = self.indexes_to_array(double_top, prices)
        return buys, sells
