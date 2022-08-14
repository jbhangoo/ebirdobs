import datetime
import json
import os

import pandas as pd
import plotly
import plotly.graph_objs as go
from pprint import pprint

from src.finance.dao import DAO

TICKERFILE = os.path.join(os.path.curdir, "data", "tickers.json")
DBFILE =  os.path.join(os.path.curdir, "data", "finance.db")

class Benchmark(object):
    def __init__(self):
        self.db = DAO(DBFILE)
        with open(TICKERFILE) as jf:
            self.benchmarks = json.load(jf)
            self.benchmark_ids = self.db.load_benchmarks(self.benchmarks)

    def get_prices_recent(self, benchmark):
        benchmark_id = self.benchmark_ids[benchmark]
        if benchmark_id:
            today = datetime.datetime.today()
            monthago = today + datetime.timedelta(days=-30)
            results = self.db.get_prices(benchmark_id, monthago, today)
            if results.status:
                return results.rows
            else:
                return pd.Series([], dtype='float64')
        else:
            return pd.Series([], dtype='float64')

    def get_charts(self):
        charts = []
        for benchmark in self.benchmarks:
            symbol = benchmark[2]
            prices = self.get_prices_recent(symbol)
            changes = [prices.values[i+1]/prices.values[i] for i in range(len(prices.values)-1)]
            data =  dict(
                    x = prices.index,  # assign x as the dataframe column 'x'
                    y = changes,
                    name = benchmark[0],
                    type = 'line'
            )

            charts.append(data)

            print(str(benchmark))
            pprint(prices)
        graphJSON = json.dumps(charts, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

    def get_prices_db(self, symbol, endDate, startDate):
        dbresults = self.db.get_prices(symbol, endDate, startDate)
        if dbresults.status:
            return dbresults.rows
        else:
            return []




