import json
from typing import List

class Ticker(object):
    def __init__(self, symbol, defn, desc):
        self.symbol = symbol
        self.definition = defn
        self.description = desc

    def __str__(self):
        return "{} ({}) - {}".format(self.definition, self.symbol, self.description)

def load_ticker_file(ticker_file) -> List[Ticker]:
    tickers = []
    with open(ticker_file) as jf:
        ticker_rows = json.load(jf)
        for ticker_row in ticker_rows:
            ticker = Ticker(ticker_row[2], ticker_row[0], ticker_row[1])
            tickers.append(ticker)
    return tickers


tickers = ["^DJI", "^GSPC"]