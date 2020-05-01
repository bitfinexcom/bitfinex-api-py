"""
Module used to describe all of the different data types
"""


class Position:
    """
    SYMBOL	string	Pair (tBTCUSD, ...).
    STATUS	string	Status (ACTIVE, CLOSED).
    AMOUNT	float	Size of the position. Positive values means a long position,
            negative values means a short position.
    BASE_PRICE	float	The price at which you entered your position.
    MARGIN_FUNDING	float	The amount of funding being used for this position.
    MARGIN_FUNDING_TYPE	int	0 for daily, 1 for term.
    PL	float	Profit & Loss
    PL_PERC	float	Profit & Loss Percentage
    PRICE_LIQ	float	Liquidation price
    LEVERAGE	float	Beta value
    """

    def __init__(self, symbol, status, amount, b_price, m_funding, m_funding_type,
                 profit_loss, profit_loss_perc, l_price, lev):
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

    @staticmethod
    def from_raw_rest_position(raw_position):
        """
        Generate a Position object from a raw position array

        @return Position
        """
        return Position(*raw_position)

    def __str__(self):
        ''' Allow us to print the Trade object in a pretty format '''
        text = "Position '{}' {} x {} <status='{}' pl={}>"
        return text.format(self.symbol, self.base_price, self.amount,
                           self.status, self.profit_loss)
