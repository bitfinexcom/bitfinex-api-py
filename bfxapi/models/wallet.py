"""
Module used to describe all of the different data types
"""


class Wallet:
    """
    Stores data relevant to a users wallet such as balance and
    currency
    """

    def __init__(self, wType, currency, balance, unsettled_interest, balance_available):
        self.type = wType
        self.currency = currency
        self.balance = balance
        self.balance_available = balance_available
        self.unsettled_interest = unsettled_interest
        self.key = "{}_{}".format(wType, currency)

    def set_balance(self, data):
        """
        Set the balance of the wallet
        """
        self.balance = data

    def set_unsettled_interest(self, data):
        """
        Set the unsettled interest of the wallet
        """
        self.unsettled_interest = data

    def __str__(self):
        return "Wallet <'{}_{}' balance='{}' balance_available='{}' unsettled='{}'>".format(
            self.type, self.currency, self.balance, self.balance_available, self.unsettled_interest)
