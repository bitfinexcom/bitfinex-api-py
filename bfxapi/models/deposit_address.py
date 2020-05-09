"""
Module used to describe a DepositAddress object
"""

class DepositModel:
    """
    Enum used to index the location of each value in a raw array
    """
    METHOD = 1
    CURRENCY = 2
    ADDRESS = 4

class DepositAddress:
    """
    [None, 'BITCOIN', 'BTC', None, '38zsUkv8q2aiXK9qsZVwepXjWeh3jKvvZw']

    METHOD string  Protocol used for funds transfer
    SYMBOL string  Currency symbol
    ADDRESS string  Deposit address for funds transfer
    """

    def __init__(self, method, currency, address):
        self.method = method
        self.currency = currency
        self.address = address

    @staticmethod
    def from_raw_deposit_address(raw_add):
        """
        Parse a raw deposit object into a DepositAddress object

        @return DepositAddress
        """
        method = raw_add[DepositModel.METHOD]
        currency = raw_add[DepositModel.CURRENCY]
        address = raw_add[DepositModel.ADDRESS]
        return DepositAddress(method, currency, address)

    def __str__(self):
        """
        Allow us to print the Transfer object in a pretty format
        """
        text = "DepositAddress <{}  method={} currency={}>"
        return text.format(self.address, self.method, self.currency)
