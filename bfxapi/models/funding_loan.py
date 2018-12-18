"""
Module used to describe all of the different data types
"""


class FundingLoanModel:
    """
    Enum used to index the location of each value in a raw array
    """
    ID = 0
    SYMBOL = 1
    SIDE = 2
    MTS_CREATE = 3
    MTS_UPDATE = 4
    AMOUNT = 5
    FLAGS = 6
    STATUS = 7
    RATE = 11
    PERIOD = 12
    MTS_OPENING = 13
    MTS_LAST_PAYOUT = 14
    NOTIFY = 15
    HIDDEN = 16
    RENEW = 18
    NO_CLOSE = 20


class FundingLoan:
    """
    ID	integer	Offer ID
    SYMBOL	string	The currency of the offer (fUSD, etc)
    SIDE	string	"Lend" or "Loan"
    MTS_CREATE	int	Millisecond Time Stamp when the offer was created
    MTS_UPDATE	int	Millisecond Time Stamp when the offer was created
    AMOUNT	float	Amount the offer is for
    FLAGS	object	future params object (stay tuned)
    STATUS	string	Offer Status: ACTIVE, EXECUTED, PARTIALLY FILLED, CANCELED
    RATE	float	Rate of the offer
    PERIOD	int	Period of the offer
    MTS_OPENING	int	Millisecond Time Stamp for when the loan was opened
    MTS_LAST_PAYOUT	int	Millisecond Time Stamp for when the last payout was made
    NOTIFY	int	0 if false, 1 if true
    HIDDEN	int	0 if false, 1 if true
    RENEW	int	0 if false, 1 if true
    NO_CLOSE	int	If funding will be returned when position is closed. 0 if false, 1 if true
    """

    def __init__(self, fid, symbol, side, mts_create, mts_update, amount, flags, status, rate,
                 period, mts_opening, mts_last_payout, notify, hidden, renew, no_close):
        # pylint: disable=invalid-name
        self.id = fid
        self.symbol = symbol
        self.side = side
        self.mts_create = mts_create
        self.mts_update = mts_update
        self.amount = amount
        self.flags = flags
        self.status = status
        self.rate = rate
        self.period = period
        self.mts_opening = mts_opening
        self.mts_last_payout = mts_last_payout
        self.notify = notify
        self.hidden = hidden
        self.renew = renew
        self.no_close = no_close

    @staticmethod
    def from_raw_loan(raw_loan):
        """
        Parse a raw funding load into a FundingLoan object

        @return FundingLoan
        """
        fid = raw_loan[FundingLoanModel.ID]
        symbol = raw_loan[FundingLoanModel.SYMBOL]
        side = raw_loan[FundingLoanModel.SIDE]
        mts_create = raw_loan[FundingLoanModel.MTS_CREATE]
        mts_update = raw_loan[FundingLoanModel.MTS_UPDATE]
        amount = raw_loan[FundingLoanModel.AMOUNT]
        flags = raw_loan[FundingLoanModel.FLAGS]
        status = raw_loan[FundingLoanModel.STATUS]
        rate = raw_loan[FundingLoanModel.RATE]
        period = raw_loan[FundingLoanModel.PERIOD]
        mts_opening = raw_loan[FundingLoanModel.MTS_OPENING]
        mts_last_payout = raw_loan[FundingLoanModel.MTS_LAST_PAYOUT]
        notify = raw_loan[FundingLoanModel.NOTIFY]
        hidden = raw_loan[FundingLoanModel.HIDDEN]
        renew = raw_loan[FundingLoanModel.RENEW]
        no_close = raw_loan[FundingLoanModel.NO_CLOSE]
        return FundingLoan(fid, symbol, side, mts_create, mts_update, amount, flags, status, rate,
                           period, mts_opening, mts_last_payout, notify, hidden, renew, no_close)

    def __str__(self):
        return "FundingLoan '{}' <id={} rate={} amount={} period={} status='{}'>".format(
            self.symbol, self.id, self.rate, self.amount, self.period, self.status)
