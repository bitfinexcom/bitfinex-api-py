"""
Module used to describe all of the different data types
"""

import datetime

class MarginInfoModel:
    """
    Enum used to index the different values in a raw margin info array
    """
    TRADABLE_BALANCE = 0
    GROSS_BALANCE = 1
    BUY = 2
    SELL = 3

class MarginInfo:
    """
    SYMBOL  string
    TRADABLE BALANCE    float
    GROSS_BALANCE	float
    BUY
    SELL
    """

    def __init__(self, symbol, tradable_balance, gross_balance, buy, sell):
        # pylint: disable=invalid-name
        self.symbol = symbol
        self.tradable_balance = tradable_balance
        self.gross_balance = gross_balance
        self.buy = buy
        self.sell = sell

    @staticmethod
    def from_raw_margin_info(raw_margin_info):
        """
        Generate a MarginInfo object from a raw margin info array
        """
        symbol = raw_margin_info[1]
        tradable_balance = raw_margin_info[2][MarginInfoModel.TRADABLE_BALANCE]
        gross_balance = raw_margin_info[2][MarginInfoModel.GROSS_BALANCE]
        buy = raw_margin_info[2][MarginInfoModel.BUY]
        sell = raw_margin_info[2][MarginInfoModel.SELL]
        return MarginInfo(symbol, tradable_balance, gross_balance, buy, sell)

    def __str__(self):
        return "Margin Info {} buy={} sell={} tradable_balance={} gross_balance={}" \
               "".format(self.symbol, self.buy, self.sell, self. tradable_balance, self. gross_balance)
