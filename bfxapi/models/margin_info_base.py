"""
Module used to describe all of the different data types
"""

import datetime

class MarginInfoBaseModel:
    """
    Enum used to index the different values in a raw margin info array
    """
    USER_PL = 0
    USER_SWAPS = 1
    MARGIN_BALANCE = 2
    MARGIN_NET = 3
    MARGIN_MIN = 4

class MarginInfoBase:
    """
    USER_PL   float
    USER_SWAPS  float
    MARGIN_BALANCE	 float
    MARGIN_NET   float
    MARGIN_MIN   float
    """

    def __init__(self, user_pl, user_swaps, margin_balance, margin_net, margin_min):
        # pylint: disable=invalid-name
        self.user_pl = user_pl
        self.user_swaps = user_swaps
        self.margin_balance = margin_balance
        self.margin_net = margin_net
        self.margin_min = margin_min

    @staticmethod
    def from_raw_margin_info(raw_margin_info):
        """
        Generate a MarginInfoBase object from a raw margin info array
        """
        user_pl = raw_margin_info[1][MarginInfoBaseModel.USER_PL]
        user_swaps = raw_margin_info[1][MarginInfoBaseModel.USER_SWAPS]
        margin_balance = raw_margin_info[1][MarginInfoBaseModel.MARGIN_BALANCE]
        margin_net = raw_margin_info[1][MarginInfoBaseModel.MARGIN_NET]
        margin_min = raw_margin_info[1][MarginInfoBaseModel.MARGIN_MIN]
        return MarginInfoBase(user_pl, user_swaps, margin_balance, margin_net, margin_min)

    def __str__(self):
        return "Margin Info Base user_pl={} user_swaps={} margin_balance={} margin_net={} margin_min={}" \
               "".format(self.user_pl, self.user_swaps, self.margin_balance, self.margin_net, self.margin_min)
