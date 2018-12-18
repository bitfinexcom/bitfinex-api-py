"""
Module used to describe all of the different data types
"""


class FundingCreditModel:
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
    POSITION_PAIR = 21


class FundingCredit:
    """
    ID	integer	Offer ID
    SYMBOL	string	The currency of the offer (fUSD, etc)
    SIDE	string	"Lend" or "Loan"
    MTS_CREATE	int	Millisecond Time Stamp when the offer was created
    MSG_UPDATE	int	Millisecond Time Stamp when the offer was updated
    AMOUNT	float	Amount the offer is for
    FLAGS	object	future params object (stay tuned)
    STATUS	string	Offer Status: ACTIVE, EXECUTED, PARTIALLY FILLED, CANCELED
    RATE	float	Rate of the offer
    PERIOD	int	Period of the offer
    MTS_OPENING	int	Millisecond Time Stamp when funding opened
    MTS_LAST_PAYOUT	int	Millisecond Time Stamp when last payout received
    NOTIFY	int	0 if false, 1 if true
    HIDDEN	int	0 if false, 1 if true
    RENEW	int	0 if false, 1 if true
    NO_CLOSE	int	0 if false, 1 if true Whether the funding will be closed when the
              position is closed
    POSITION_PAIR	string	Pair of the position that the funding was used for
    """

    def __init__(self, fid, symbol, side, mts_create, mts_update, amount, flags, status, rate,
                 period, mts_opening, mts_last_payout, notify, hidden, renew, no_close,
                 position_pair):
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
        self.position_pair = position_pair

    @staticmethod
    def from_raw_credit(raw_credit):
        """
        Parse a raw credit object into a FundingCredit object

        @return FundingCredit
        """
        fid = raw_credit[FundingCreditModel.ID]
        symbol = raw_credit[FundingCreditModel.SYMBOL]
        side = raw_credit[FundingCreditModel.SIDE]
        mts_create = raw_credit[FundingCreditModel.MTS_CREATE]
        mts_update = raw_credit[FundingCreditModel.MTS_UPDATE]
        amount = raw_credit[FundingCreditModel.AMOUNT]
        flags = raw_credit[FundingCreditModel.FLAGS]
        status = raw_credit[FundingCreditModel.STATUS]
        rate = raw_credit[FundingCreditModel.RATE]
        period = raw_credit[FundingCreditModel.PERIOD]
        mts_opening = raw_credit[FundingCreditModel.MTS_OPENING]
        mts_last_payout = raw_credit[FundingCreditModel.MTS_LAST_PAYOUT]
        notify = raw_credit[FundingCreditModel.NOTIFY]
        hidden = raw_credit[FundingCreditModel.HIDDEN]
        renew = raw_credit[FundingCreditModel.RENEW]
        no_close = raw_credit[FundingCreditModel.NO_CLOSE]
        position_pair = raw_credit[FundingCreditModel.POSITION_PAIR]
        return FundingCredit(fid, symbol, side, mts_create, mts_update, amount,
                             flags, status, rate, period, mts_opening, mts_last_payout,
                             notify, hidden, renew, no_close, position_pair)

    def __str__(self):
        string = "FundingCredit '{}' <id={} rate={} amount={} period={} status='{}'>"
        return string.format(self.symbol, self.id, self.rate, self.amount,
                             self.period, self.status)
