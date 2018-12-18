"""
Module used to describe all of the different data types
"""

import zlib


def prepare_price(price):
    """
    Convert the price to an acceptable format
    """
    # convert to 4 significant figures
    prep_price = '{0:.4f}'.format(price)
    # remove decimal place if zero float
    return '{0:g}'.format(float(prep_price))


class OrderBook:
    """
    Object used to store the state of the orderbook. This can then be used
    in one of two ways. To get the checksum of the book or so get the bids/asks
    of the book
    """

    def __init__(self):
        self.asks = []
        self.bids = []

    def get_bids(self):
        """
        Get all of the bids from the orderbook

        @return bids Array
        """
        return self.bids

    def get_asks(self):
        """
        Get all of the asks from the orderbook

        @return asks Array
        """
        return self.asks

    def update_from_snapshot(self, data):
        """
        Update the orderbook with a raw orderbook snapshot
        """
        for order in data:
            if len(order) == 4:
                if order[3] < 0:
                    self.bids += [order]
                else:
                    self.asks += [order]
            else:
                if order[2] < 0:
                    self.asks += [order]
                else:
                    self.bids += [order]

    def update_with(self, order):
        """
        Update the orderbook with a single update
        """
        if len(order) == 4:
            amount = order[3]
            count = order[2]
            side = self.bids if amount < 0 else self.asks
        else:
            amount = order[2]
            side = self.asks if amount < 0 else self.bids
            count = order[1]
        price = order[0]

        # if first item in ordebook
        if len(side) == 0:
            side += [order]
            return

        # match price level
        for index, s_order in enumerate(side):
            s_price = s_order[0]
            if s_price == price:
                if count == 0:
                    del side[index]
                    return
                # remove but add as new below
                del side[index]

        # if ob is initialised w/o all price levels
        if count == 0:
            return

        # add to book and sort lowest to highest
        side += [order]
        side.sort(key=lambda x: x[0], reverse=not amount < 0)
        return

    def checksum(self):
        """
        Generate a CRC32 checksum of the orderbook
        """
        data = []
        # take set of top 25 bids/asks
        for index in range(0, 25):
            if index < len(self.bids):
                bid = self.bids[index]
                price = bid[0]
                amount = bid[3] if len(bid) == 4 else bid[2]
                data += [prepare_price(price)]
                data += [str(amount)]
            if index < len(self.asks):
                ask = self.asks[index]
                price = ask[0]
                amount = ask[3] if len(ask) == 4 else ask[2]
                data += [prepare_price(price)]
                data += [str(amount)]
        checksum_str = ':'.join(data)
        # calculate checksum and force signed integer
        checksum = zlib.crc32(checksum_str.encode('utf8')) & 0xffffffff
        return checksum
