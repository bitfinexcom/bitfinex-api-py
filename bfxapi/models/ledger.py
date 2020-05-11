"""
Module used to describe a ledger object
"""

class LedgerModel:
    """
    Enum used to index the location of each value in a raw array
    """
    ID = 0
    CURRENCY = 1
    MTS = 3
    AMOUNT = 5
    BALANCE = 6
    DESCRIPTION = 8

class Ledger:
    """
    ID int
    CURRENCY string Currency (BTC, etc)
    PLACEHOLDER
    MTS	int	Millisecond Time Stamp of the update
    PLACEHOLDER
    AMOUNT string  Amount of funds to ledger
    BALANCE string  Amount of funds to ledger
    PLACEHOLDER
    DESCRIPTION
    """

    def __init__(self, currency, mts, amount, balance, description):
        self.currency = currency
        self.mts = mts
        self.amount = amount
        self.balance = balance
        self.description = description

    @staticmethod
    def from_raw_ledger(raw_ledger):
        """
        Parse a raw ledger object into a Ledger object

        @return Ledger
        """
        currency = raw_ledger[LedgerModel.CURRENCY]
        mts = raw_ledger[LedgerModel.MTS]
        amount = raw_ledger[LedgerModel.AMOUNT]
        balance = raw_ledger[LedgerModel.BALANCE]
        description = raw_ledger[LedgerModel.DESCRIPTION]
        return Ledger(currency, mts, amount, balance, description)

    def __str__(self):
        ''' Allow us to print the Ledger object in a pretty format '''
        text = "Ledger <{} {} balance:{} '{}' mts={}>"
        return text.format(self.amount, self.currency, self.balance,
                           self.description, self.mts)
