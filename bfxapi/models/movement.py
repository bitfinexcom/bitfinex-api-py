"""
Module used to describe movement data types
"""

import time
import datetime

class MovementModel:
    """
    Enum used index the different values in a raw movement array
    """

    ID = 0
    CURRENCY = 1
    CURRENCY_NAME	= 2
    MTS_STARTED	= 5
    MTS_UPDATED = 6
    STATUS = 9
    AMOUNT = 12
    FEES = 13
    DESTINATION_ADDRESS	= 16
    TRANSACTION_ID = 20

class Movement:

    """
    ID	String	Movement identifier
    CURRENCY	String	The symbol of the currency (ex. "BTC")
    CURRENCY_NAME	String	The extended name of the currency (ex. "BITCOIN")
    MTS_STARTED	Date	Movement started at
    MTS_UPDATED	Date	Movement last updated at
    STATUS	String	Current status
    AMOUNT	String	Amount of funds moved
    FEES	String	Tx Fees applied
    DESTINATION_ADDRESS	String	Destination address
    TRANSACTION_ID	String	Transaction identifier
    """

    def __init__(self, mid, currency, mts_started, mts_updated, status, amount, fees, dst_address, tx_id):
        self.id = mid
        self.currency = currency
        self.mts_started = mts_started
        self.mts_updated = mts_updated
        self.status = status
        self.amount = amount
        self.fees = fees
        self.dst_address = dst_address
        self.tx_id = tx_id

        self.date = datetime.datetime.fromtimestamp(mts_started/1000.0)


    @staticmethod
    def from_raw_movement(raw_movement):
        """
        Parse a raw movement object into a Movement object
        @return Movement
        """

        mid = raw_movement[MovementModel.ID]
        currency = raw_movement[MovementModel.CURRENCY]
        mts_started = raw_movement[MovementModel.MTS_STARTED]
        mts_updated = raw_movement[MovementModel.MTS_UPDATED]
        status = raw_movement[MovementModel.STATUS]
        amount = raw_movement[MovementModel.AMOUNT]
        fees = raw_movement[MovementModel.FEES]
        dst_address = raw_movement[MovementModel.DESTINATION_ADDRESS]
        tx_id = raw_movement[MovementModel.TRANSACTION_ID]

        return Movement(mid, currency, mts_started, mts_updated, status, amount, fees, dst_address, tx_id)

    def __str__(self):
        ''' Allow us to print the Movement object in a pretty format '''
        text = "Movement <'{}' amount={} fees={} mts_created={} mts_updated={} status='{}' destination_address={} transaction_id={}>"
        return text.format(self.currency, self.amount, self.fees,
                           self.mts_started, self.mts_updated, self.status, self.dst_address, self.tx_id)