"""
Module used to describe all of the different data types
"""

class FundingOfferTypes:
    """
    Enum used to define the different funding offer types
    """
    LIMIT = 'LIMIT'
    FRR_DELTA = 'FRRDELTAVAR'

class FundingOfferModel:
    """
    Enum used to index the location of each value in a raw array
    """
    ID = 0
    SYMBOL = 1
    MTS_CREATE = 2
    MTS_UPDATED = 3
    AMOUNT = 4
    AMOUNT_ORIG = 5
    TYPE = 6
    FLAGS = 9
    STATUS = 10
    RATE = 14
    PERIOD = 15
    NOTFIY = 16
    HIDDEN = 17
    RENEW = 19


class FundingOffer:
    """
    ID	integer	Offer ID
    SYMBOL	string	The currency of the offer (fUSD, etc)
    MTS_CREATED	int	Millisecond Time Stamp when the offer was created
    MSG_UPDATED	int	Millisecond Time Stamp when the offer was created
    AMOUNT	float	Amount the offer is for
    AMOUNT_ORIG	float	Amount the offer was entered with originally
    TYPE	string	"lend" or "loan"
    FLAGS	object	future params object (stay tuned)
    STATUS	string	Offer Status: ACTIVE, EXECUTED, PARTIALLY FILLED, CANCELED
    RATE	float	Rate of the offer
    PERIOD	int	Period of the offer
    NOTIFY	int	0 if false, 1 if true
    HIDDEN	int	0 if false, 1 if true
    RENEW	int	0 if false, 1 if true
    """

    Type = FundingOfferTypes()

    def __init__(self, fid, symbol, mts_create, mts_updated, amount, amount_orig, f_type,
                 flags, status, rate, period, notify, hidden, renew):
        # pylint: disable=invalid-name
        self.id = fid
        self.symbol = symbol
        self.mts_create = mts_create
        self.mts_updated = mts_updated
        self.amount = amount
        self.amount_orig = amount_orig
        self.f_type = f_type
        self.flags = flags
        self.status = status
        self.rate = rate
        self.period = period
        self.notify = notify
        self.hidden = hidden
        self.renew = renew

    @staticmethod
    def from_raw_offer(raw_offer):
        """
        Parse a raw funding offer into a RawFunding object

        @return FundingOffer
        """
        oid = raw_offer[FundingOfferModel.ID]
        symbol = raw_offer[FundingOfferModel.SYMBOL]
        mts_create = raw_offer[FundingOfferModel.MTS_CREATE]
        mts_updated = raw_offer[FundingOfferModel.MTS_UPDATED]
        amount = raw_offer[FundingOfferModel.AMOUNT]
        amount_orig = raw_offer[FundingOfferModel.AMOUNT_ORIG]
        f_type = raw_offer[FundingOfferModel.TYPE]
        flags = raw_offer[FundingOfferModel.FLAGS]
        status = raw_offer[FundingOfferModel.STATUS]
        rate = raw_offer[FundingOfferModel.RATE]
        period = raw_offer[FundingOfferModel.PERIOD]
        notify = raw_offer[FundingOfferModel.NOTFIY]
        hidden = raw_offer[FundingOfferModel.HIDDEN]
        renew = raw_offer[FundingOfferModel.RENEW]
        return FundingOffer(oid, symbol, mts_create, mts_updated, amount,
                            amount_orig, f_type, flags, status, rate, period, notify, hidden, renew)

    def __str__(self):
        return "FundingOffer '{}' <id={} rate={} period={} status='{}'>".format(
            self.symbol, self.id, self.rate, self.period, self.status)
