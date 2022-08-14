class Ticker(object):
    def __init__(self, symbol, defn, desc):
        self.symbol = symbol
        self.definition = defn
        self.description = desc

    def __str__(self):
        return "{} ({}) - {}".format(self.definition, self.symbol, self.description)

tickers = ["^DJI", "^GSPC"]