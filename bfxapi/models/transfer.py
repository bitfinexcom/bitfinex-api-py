"""
Module used to describe a transfer object
"""

class TransferModel:
    """
    Enum used to index the location of each value in a raw array
    """
    MTS = 0
    W_FROM = 1
    W_TO = 2
    C_FROM = 4
    C_TO = 5
    AMOUNT = 7

class Transfer:
    """
    MTS	int	Millisecond Time Stamp of the update
    WALLET_FROM string	Wallet name (exchange, margin, funding)
    WALLET_TO string	Wallet name (exchange, margin, funding)
    CURRENCY_FROM 	string Currency (BTC, etc)
    CURRENCY_TO	 string Currency (BTC, etc)
    AMOUNT string  Amount of funds to transfer
    """

    def __init__(self, mts, wallet_from, wallet_to, currency_from, currency_to, amount):
        self.mts = mts
        self.wallet_from = wallet_from
        self.wallet_to = wallet_to
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.amount = amount

    @staticmethod
    def from_raw_transfer(raw_transfer):
        """
        Parse a raw transfer object into a Transfer object

        @return Transfer
        """
        mts = raw_transfer[TransferModel.MTS]
        wallet_from = raw_transfer[TransferModel.W_FROM]
        wallet_to = raw_transfer[TransferModel.W_TO]
        currency_from = raw_transfer[TransferModel.C_FROM]
        currency_to = raw_transfer[TransferModel.C_TO]
        amount = raw_transfer[TransferModel.AMOUNT]
        return Transfer(mts, wallet_from, wallet_to, currency_from, currency_to, amount)

    def __str__(self):
        """
        Allow us to print the Transfer object in a pretty format
        """
        text = "Transfer <{} from {} ({}) to {} ({}) mts={}>"
        return text.format(self.amount, self.wallet_from, self.currency_from,
                           self.wallet_to, self.currency_to, self.mts)
