"""
Module used to describe all of the different data types
"""

class TickerModel:
    """
    Enum used to index the different values in a raw ticker array
    """
    BID = 0
    BID_SIZE = 1
    ASK = 2
    ASK_SIZE = 3
    DAILY_CHANGE = 4
    DAILY_CHANGE_PERCENT = 5
    LAST_PRICE = 6
    VOLUME = 7
    HIGH = 8
    LOW = 9

class Ticker:
    """
    BID	float	    Price of last highest bid
    BID_SIZE	    float	Sum of the 25 highest bid sizes
    ASK	float	    Price of last lowest ask
    ASK_SIZE	    float	Sum of the 25 lowest ask sizes
    DAILY_CHANGE	float	Amount that the last price has changed since yesterday
    DAILY_CHANGE_PERCENT	float	Relative price change since yesterday (*100 for percentage change)
    LAST_PRICE	    float	Price of the last trade
    VOLUME	        float	Daily volume
    HIGH	        float	Daily high
    LOW	            float	Daily low
    """

    def __init__(self, pair, bid, bid_size, ask, ask_size, daily_change, daily_change_rel,
                 last_price, volume, high, low):
        self.pair = pair
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size
        self.daily_change = daily_change
        self.daily_change_rel = daily_change_rel
        self.last_price = last_price
        self.volume = volume
        self.high = high
        self.low = low

    @staticmethod
    def from_raw_ticker(raw_ticker, pair):
        """
        Generate a Ticker object from a raw ticker array
        """
        # [72128,[6914.5,28.123061460000002,6914.6,22.472037289999996,175.8,0.0261,6915.7,
        # 6167.26141685,6964.2,6710.8]]

        return Ticker(
            pair,
            raw_ticker[TickerModel.BID],
            raw_ticker[TickerModel.BID_SIZE],
            raw_ticker[TickerModel.ASK],
            raw_ticker[TickerModel.ASK_SIZE],
            raw_ticker[TickerModel.DAILY_CHANGE],
            raw_ticker[TickerModel.DAILY_CHANGE_PERCENT],
            raw_ticker[TickerModel.LAST_PRICE],
            raw_ticker[TickerModel.VOLUME],
            raw_ticker[TickerModel.HIGH],
            raw_ticker[TickerModel.LOW],
        )

    def __str__(self):
        return "Ticker '{}' <last='{}' volume={}>".format(
            self.pair, self.last_price, self.volume)
