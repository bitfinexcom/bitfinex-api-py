"""
Module used to describe a withdraw object
"""

class WithdrawModel:
    """
    Enum used to index the location of each value in a raw array
    """
    ID = 0
    METHOD = 2
    WALLET = 4
    AMOUNT = 5
    FEE = 7

class Withdraw:
    """
    [13063236, None, 'tetheruse', None, 'exchange', 5, None, None, 0.00135]

    MTS	int	Millisecond Time Stamp of the update
    WALLET_FROM string	Wallet name (exchange, margin, funding)
    WALLET_TO string	Wallet name (exchange, margin, funding)
    CURRENCY_FROM 	string Currency (BTC, etc)
    CURRENCY_TO	 string Currency (BTC, etc)
    AMOUNT string  Amount of funds to transfer
    """

    def __init__(self, w_id, method, wallet, amount, fee=0):
        self.id = w_id
        self.method = method
        self.wallet = wallet
        self.amount = amount
        self.fee = fee

    @staticmethod
    def from_raw_withdraw(raw_withdraw):
        """
        Parse a raw withdraw object into a Withdraw object

        @return Withdraw
        """
        w_id = raw_withdraw[WithdrawModel.ID]
        method = raw_withdraw[WithdrawModel.METHOD]
        wallet = raw_withdraw[WithdrawModel.WALLET]
        amount = raw_withdraw[WithdrawModel.AMOUNT]
        return Withdraw(w_id, method, wallet, amount)

    def __str__(self):
        """
        Allow us to print the Withdraw object in a pretty format
        """
        text = "Withdraw <id={} from {} ({}) amount={} fee={}>"
        return text.format(self.id, self.wallet, self.method, self.amount,
                           self.fee)
