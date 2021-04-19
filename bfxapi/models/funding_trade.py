"""
Module used to describe all of the different data types
"""

class FundingTradeModel:
    """
    Enum used to index the different values in a raw funding trade array
    """
    ID = 0
    SYMBOL = 1
    MTS_CREATE = 2
    OFFER_ID = 3
    AMOUNT = 4
    RATE = 5
    PERIOD = 6
    MAKER = 7

class FundingTrade:
    """
    ID	integer	Offer ID
    SYMBOL	string	The currency of the offer (fUSD, etc)
    MTS_CREATE	int	Millisecond Time Stamp when the offer was created
    OFFER_ID	int	The ID of the offer
    AMOUNT	float	Amount the offer is for
    RATE	float	Rate of the offer
    PERIOD	int	Period of the offer
    MAKER	int	1 if true, -1 if false Whether the offer took liquidity off the funding book
    """

    def __init__(self, tid, symbol, mts_create, offer_id, amount, rate, period, maker):
        self.tid = tid
        self.symbol = symbol
        self.mts_create = mts_create
        self.offer_id = offer_id
        self.amount = amount
        self.rate = rate
        self.period = period
        self.maker = maker

    @staticmethod
    def from_raw_rest_trade(raw_trade):
        """
        Generate a Ticker object from a raw ticker array
        """
        # [[636040,"fUST",1574077528000,41237922,-100,0.0024,2,null]]
        return FundingTrade(
            raw_trade[FundingTradeModel.ID],
            raw_trade[FundingTradeModel.SYMBOL],
            raw_trade[FundingTradeModel.MTS_CREATE],
            raw_trade[FundingTradeModel.OFFER_ID],
            raw_trade[FundingTradeModel.AMOUNT],
            raw_trade[FundingTradeModel.RATE],
            raw_trade[FundingTradeModel.PERIOD],
            raw_trade[FundingTradeModel.MAKER]
        )

    def __str__(self):
        return "FundingTrade '{}' x {} @ {} for {} days <maker='{}'>".format(
            self.symbol, self.amount, self.rate, self.period, self.maker)
