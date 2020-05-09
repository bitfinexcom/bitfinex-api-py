"""
Module used to describe all of the different data types
"""
class PositionModel:
    """
    Enum used to index the different values in a raw position array
    """
    SYMBOL = 0
    STATUS = 1
    AMOUNT = 2
    BASE_PRICE = 3
    MARGIN_FUNDING = 4
    MARGIN_FUNDING_TYPE = 5
    PL = 6
    PL_PERC = 7
    PRICE_LIQ = 8
    LEVERAGE = 9
    # _PLACEHOLDER,
    POSITION_ID = 11
    MTS_CREATE = 12
    MTS_UPDATE = 13
    # _PLACEHOLDER
    TYPE = 15
    # _PLACEHOLDER,
    COLLATERAL = 17
    COLLATERAL_MIN = 18
    META = 19

class Position:
    """
    SYMBOL	        string	Pair (tBTCUSD, …).
    STATUS	        string	Status (ACTIVE, CLOSED).
    ±AMOUNT	        float	Size of the position. A positive value indicates a
                    long position; a negative value indicates a short position.
    BASE_PRICE	    float	Base price of the position. (Average traded price
                    of the previous orders of the position)
    MARGIN_FUNDING	float	The amount of funding being used for this position.
    MARGIN_FUNDING_TYPE	int	0 for daily, 1 for term.
    PL	            float	Profit & Loss
    PL_PERC	        float	Profit & Loss Percentage
    PRICE_LIQ	    float	Liquidation price
    LEVERAGE	    float	Leverage used for the position
    POSITION_ID	    int64	Position ID
    MTS_CREATE	    int	Millisecond timestamp of creation
    MTS_UPDATE	    int	Millisecond timestamp of update
    TYPE	        int	Identifies the type of position, 0 = Margin position,
                    1 = Derivatives position
    COLLATERAL	    float	The amount of collateral applied to the open position
    COLLATERAL_MIN	float	The minimum amount of collateral required for the position
    META	        json string	Additional meta information about the position
    """

    def __init__(self, symbol, status, amount, b_price, m_funding, m_funding_type,
                 profit_loss, profit_loss_perc, l_price, lev, pid, mts_create, mts_update,
                 p_type, collateral, collateral_min, meta):
        self.symbol = symbol
        self.status = status
        self.amount = amount
        self.base_price = b_price
        self.margin_funding = m_funding
        self.margin_funding_type = m_funding_type
        self.profit_loss = profit_loss
        self.profit_loss_percentage = profit_loss_perc
        self.liquidation_price = l_price
        self.leverage = lev
        self.id = pid
        self.mts_create = mts_create
        self.mts_update = mts_update
        self.type = p_type
        self.collateral = collateral
        self.collateral_min = collateral_min
        self.meta = meta

    @staticmethod
    def from_raw_rest_position(raw_position):
        """
        Generate a Position object from a raw position array

        @return Position
        """
        sym = raw_position[PositionModel.SYMBOL]
        status = raw_position[PositionModel.STATUS]
        amnt = raw_position[PositionModel.AMOUNT]
        b_price = raw_position[PositionModel.BASE_PRICE]
        m_fund = raw_position[PositionModel.MARGIN_FUNDING]
        m_fund_t = raw_position[PositionModel.MARGIN_FUNDING_TYPE]
        pl = raw_position[PositionModel.PL]
        pl_prc = raw_position[PositionModel.PL_PERC]
        l_price = raw_position[PositionModel.PRICE_LIQ]
        lev = raw_position[PositionModel.LEVERAGE]
        pid = raw_position[PositionModel.POSITION_ID]
        mtsc = raw_position[PositionModel.MTS_CREATE]
        mtsu = raw_position[PositionModel.MTS_UPDATE]
        ptype = raw_position[PositionModel.TYPE]
        coll = raw_position[PositionModel.COLLATERAL]
        coll_min = raw_position[PositionModel.COLLATERAL_MIN]
        meta = raw_position[PositionModel.META]

        return Position(sym, status, amnt, b_price, m_fund, m_fund_t, pl, pl_prc, l_price,
                        lev, pid, mtsc, mtsu, ptype, coll, coll_min, meta)

    def __str__(self):
        """
        Allow us to print the Trade object in a pretty format
        """
        text = "Position '{}' {} x {} <status='{}' pl={}>"
        return text.format(self.symbol, self.base_price, self.amount,
                           self.status, self.profit_loss)
