"""
Module used to describe all of the different order data types
"""

import time
import datetime

class OrderType:
    """
    Enum used to describe all of the different order types available for use
    """
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'
    STOP_LIMIT = 'STOP LIMIT'
    TRAILING_STOP = 'TRAILING STOP'
    FILL_OR_KILL = 'FOK'
    EXCHANGE_MARKET = 'EXCHANGE MARKET'
    EXCHANGE_LIMIT = 'EXCHANGE LIMIT'
    EXCHANGE_STOP = 'EXCHANGE STOP'
    EXCHANGE_STOP_LIMIT = 'EXCHANGE STOP LIMIT'
    EXCHANGE_TRAILING_STOP = 'EXCHANGE TRAILING STOP'
    EXCHANGE_FILL_OR_KILL = 'EXCHANGE FOK'


LIMIT_ORDERS = [OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.EXCHANGE_LIMIT,
                OrderType.EXCHANGE_STOP_LIMIT, OrderType.FILL_OR_KILL,
                OrderType.EXCHANGE_FILL_OR_KILL]


class OrderSide:
    """
    Enum used to describe the different directions of an order
    """
    BUY = 'buy'
    SELL = 'sell'


class OrderClosedModel:
    """
    Enum used to index the different values in a raw order array
    """
    ID = 0
    GID = 1
    CID = 2
    SYMBOL = 3
    MTS_CREATE = 4
    MTS_UPDATE = 5
    AMOUNT = 6
    AMOUNT_ORIG = 7
    TYPE = 8
    TYPE_PREV = 9
    FLAGS = 12
    STATUS = 13
    PRICE = 16
    PRICE_AVG = 17
    PRICE_TRAILING = 18
    PRICE_AUX_LIMIT = 19
    NOTIFY = 23
    PLACE_ID = 25
    META = 31


class OrderFlags:
    """
    Enum used to explain the different values that can be passed in
    as flags
    """
    HIDDEN = 64
    CLOSE = 512
    REDUCE_ONLY = 1024
    POST_ONLY = 4096
    OCO = 16384


def now_in_mills():
    """
    Gets the current time in milliseconds
    """
    return int(round(time.time() * 1000))


class Order:
    """
    ID	int64	Order ID
    GID	int	Group ID
    CID	int	Client Order ID
    SYMBOL	string	Pair (tBTCUSD, ...)
    MTS_CREATE	int	Millisecond timestamp of creation
    MTS_UPDATE	int	Millisecond timestamp of update
    AMOUNT	float	Positive means buy, negative means sell.
    AMOUNT_ORIG	float	Original amount
    TYPE	string	The type of the order: LIMIT, MARKET, STOP, TRAILING STOP,
      EXCHANGE MARKET, EXCHANGE LIMIT, EXCHANGE STOP, EXCHANGE TRAILING STOP, FOK, EXCHANGE FOK.
    TYPE_PREV	string	Previous order type
    FLAGS	int	Upcoming Params Object (stay tuned)
    ORDER_STATUS	string	Order Status: ACTIVE, EXECUTED, PARTIALLY FILLED, CANCELED
    PRICE	float	Price
    PRICE_AVG	float	Average price
    PRICE_TRAILING	float	The trailing price
    PRICE_AUX_LIMIT	float	Auxiliary Limit price (for STOP LIMIT)
    HIDDEN	int	1 if Hidden, 0 if not hidden
    PLACED_ID	int	If another order caused this order to be placed (OCO) this will be that other
    order's ID
    """

    Type = OrderType()
    Side = OrderSide()
    Flags = OrderFlags()

    def __init__(self, oid, gid, cid, symbol, mts_create, mts_update, amount,
                 amount_orig, o_type, typePrev, flags, status, price, price_avg,
                 price_trailing, price_aux_limit, notfiy, place_id, meta):
        self.id = oid # pylint: disable=invalid-name
        self.gid = gid
        self.cid = cid
        self.symbol = symbol
        self.mts_create = mts_create
        self.mts_update = mts_update
        self.amount = amount
        self.amount_orig = amount_orig
        if self.amount_orig > 0:
            self.amount_filled = amount_orig - amount
        else:
            self.amount_filled = -(abs(amount_orig) - abs(amount))
        self.type = o_type
        self.type_prev = typePrev
        self.flags = flags
        self.status = status
        self.price = price
        self.price_avg = price_avg
        self.price_trailing = price_trailing
        self.price_aux_limit = price_aux_limit
        self.notfiy = notfiy
        self.place_id = place_id
        self.tag = ""
        self.fee = 0
        self.is_pending_bool = True
        self.is_confirmed_bool = False
        self.is_open_bool = False
        self.meta = meta or {}

        self.date = datetime.datetime.fromtimestamp(mts_create/1000.0)
        # if cancelled then priceAvg wont exist
        if price_avg:
            # check if order is taker or maker
            if self.type in LIMIT_ORDERS:
                self.fee = (price_avg * abs(self.amount_filled)) * 0.001
            else:
                self.fee = (price_avg * abs(self.amount_filled)) * 0.002

    @staticmethod
    def from_raw_order(raw_order):
        """
        Parse a raw order object into an Order object

        @return Order
        """
        oid = raw_order[OrderClosedModel.ID]
        gid = raw_order[OrderClosedModel.GID]
        cid = raw_order[OrderClosedModel.CID]
        symbol = raw_order[OrderClosedModel.SYMBOL]
        mts_create = raw_order[OrderClosedModel.MTS_CREATE]
        mts_update = raw_order[OrderClosedModel.MTS_UPDATE]
        amount = raw_order[OrderClosedModel.AMOUNT]
        amount_orig = raw_order[OrderClosedModel.AMOUNT_ORIG]
        o_type = raw_order[OrderClosedModel.TYPE]
        type_prev = raw_order[OrderClosedModel.TYPE_PREV]
        flags = raw_order[OrderClosedModel.FLAGS]
        status = raw_order[OrderClosedModel.STATUS]
        price = raw_order[OrderClosedModel.PRICE]
        price_avg = raw_order[OrderClosedModel.PRICE_AVG]
        price_trailing = raw_order[OrderClosedModel.PRICE_TRAILING]
        price_aux_limit = raw_order[OrderClosedModel.PRICE_AUX_LIMIT]
        notfiy = raw_order[OrderClosedModel.NOTIFY]
        place_id = raw_order[OrderClosedModel.PLACE_ID]
        meta = raw_order[OrderClosedModel.META] or {}

        return Order(oid, gid, cid, symbol, mts_create, mts_update, amount,
                     amount_orig, o_type, type_prev, flags, status, price, price_avg,
                     price_trailing, price_aux_limit, notfiy, place_id, meta)

    @staticmethod
    def from_raw_order_snapshot(raw_order_snapshot):
        """
        Parse a raw order snapshot array into an array of order objects

        @return Orders: array of order objects
        """
        parsed_orders = []
        for raw_order in raw_order_snapshot:
            parsed_orders += [Order.from_raw_order(raw_order)]
        return parsed_orders

    def set_confirmed(self):
        """
        Set the state of the order to be confirmed
        """
        self.is_pending_bool = False
        self.is_confirmed_bool = True

    def set_open_state(self, is_open):
        """
        Set the is_open state of the order
        """
        self.is_open_bool = is_open

    def is_open(self):
        """
        Check if the order is still open

        @return bool: True if order open else False
        """
        return self.is_open_bool

    def is_pending(self):
        """
        Check if the state of the order is still pending

        @return bool: True if is pending else False
        """
        return self.is_pending_bool

    def is_confirmed(self):
        """
        Check if the order has been confirmed by the bitfinex api

        @return bool: True if has been confirmed else False
        """
        return self.is_confirmed_bool

    def __str__(self):
        """
        Allow us to print the Order object in a pretty format
        """
        text = "Order <'{}' amount_orig={} amount_filled={} mts_create={} status='{}' id={}>"
        return text.format(self.symbol, self.amount_orig, self.amount_filled,
                           self.mts_create, self.status, self.id)
