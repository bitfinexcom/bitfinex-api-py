"""
Module used to describe all of the different data types
"""

class FundingTickerModel:
    """
    Enum used to index the different values in a raw funding ticker array
    """
    FRR = 0
    BID = 1
    BID_PERIOD = 2
    BID_SIZE = 3
    ASK = 4
    ASK_PERIOD = 5
    ASK_SIZE = 6
    DAILY_CHANGE = 7
    DAILY_CHANGE_PERC = 8
    LAST_PRICE = 9
    VOLUME = 10
    HIGH = 11
    LOW = 12
    # _PLACEHOLDER,
    # _PLACEHOLDER,
    FRR_AMOUNT_AVAILABLE = 15

class FundingTicker:
    """
    FRR	        float	Flash Return Rate - average of all fixed rate funding over the last hour
                (funding tickers only)
    BID	        float	Price of last highest bid
    BID_PERIOD	int	Bid period covered in days (funding tickers only)
    BID_SIZE	float	Sum of the 25 highest bid sizes
    ASK	float	Price of last lowest ask
    ASK_PERIOD	int	Ask period covered in days (funding tickers only)
    ASK_SIZE	float	Sum of the 25 lowest ask sizes
    DAILY_CHANGE	float	Amount that the last price has changed since yesterday
    DAILY_CHANGE_RELATIVE	float	Relative price change since yesterday
                            (*100 for percentage change)
    LAST_PRICE	float	Price of the last trade
    VOLUME	    float	Daily volume
    HIGH	    float	Daily high
    LOW	        float	Daily low
    FRR_AMOUNT_AVAILABLE	float	The amount of funding that is available at the
                Flash Return Rate (funding tickers only)
    """

    def __init__(self, pair, frr, bid, bid_period, bid_size, ask, ask_period, ask_size,
                 daily_change, daily_change_perc, last_price, volume, high, low, frr_amount_avail):
        self.pair = pair
        self.frr = frr
        self.bid = bid
        self.bid_period = bid_period
        self.bid_size = bid_size
        self.ask = ask
        self.ask_period = ask_period
        self.ask_size = ask_size
        self.daily_change = daily_change
        self.daily_change_perc = daily_change_perc
        self.last_price = last_price
        self.volume = volume
        self.high = high
        self.low = low
        self.frr_amount_available = frr_amount_avail

    @staticmethod
    def from_raw_ticker(raw_ticker, pair):
        """
        Generate a Ticker object from a raw ticker array
        """
        # [72128,[6914.5,28.123061460000002,6914.6,22.472037289999996,175.8,0.0261,6915.7,
        # 6167.26141685,6964.2,6710.8]]

        return FundingTicker(
            pair,
            raw_ticker[FundingTickerModel.FRR],
            raw_ticker[FundingTickerModel.BID],
            raw_ticker[FundingTickerModel.BID_PERIOD],
            raw_ticker[FundingTickerModel.BID_SIZE],
            raw_ticker[FundingTickerModel.ASK],
            raw_ticker[FundingTickerModel.ASK_PERIOD],
            raw_ticker[FundingTickerModel.ASK_SIZE],
            raw_ticker[FundingTickerModel.DAILY_CHANGE],
            raw_ticker[FundingTickerModel.DAILY_CHANGE_PERC],
            raw_ticker[FundingTickerModel.LAST_PRICE],
            raw_ticker[FundingTickerModel.VOLUME],
            raw_ticker[FundingTickerModel.HIGH],
            raw_ticker[FundingTickerModel.LOW],
            raw_ticker[FundingTickerModel.FRR_AMOUNT_AVAILABLE]
        )

    def __str__(self):
        return "FundingTicker '{}' <last='{}' volume={}>".format(
            self.pair, self.last_price, self.volume)
