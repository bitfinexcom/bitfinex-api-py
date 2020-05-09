"""
Module used to describe all of the different notification data types
"""

from .order import Order
from .funding_offer import FundingOffer
from .transfer import Transfer
from .deposit_address import DepositAddress
from .withdraw import Withdraw

class NotificationModal:
    """
    Enum used index the different values in a raw order array
    """
    MTS = 0
    TYPE = 1
    MESSAGE_ID = 2
    NOTIFY_INFO = 4
    CODE = 5
    STATUS = 6
    TEXT = 7

class NotificationError:
    """
    Enum used to hold the error response statuses
    """
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    FAILURE = "FAILURE"

class NotificationTypes:
    """
    Enum used to hold the different notification types
    """
    ORDER_NEW_REQ = "on-req"
    ORDER_CANCELED_REQ = "oc-req"
    ORDER_UPDATED_REQ = "ou-req"
    FUNDING_OFFER_NEW = "fon-req"
    FUNDING_OFFER_CANCEL = "foc-req"
    ACCOUNT_TRANSFER = "acc_tf"
    ACCOUNT_DEPOSIT = "acc_dep"
    ACCOUNT_WITHDRAW_REQ = "acc_wd-req"
    # uca ?
    # pm-req ?


class Notification:
    """
    MTS	int	Millisecond Time Stamp of the update
    TYPE string	Purpose of notification ('on-req', 'oc-req', 'uca', 'fon-req', 'foc-req')
    MESSAGE_ID	int	unique ID of the message
    NOTIFY_INFO	array/object	A message containing information regarding the notification
    CODE null or integer	Work in progress
    STATUS string	Status of the notification; it may vary over time (SUCCESS, ERROR, FAILURE, ...)
    TEXT string	Text of the notification
    """

    def __init__(self, mts, notify_type, message_id, notify_info, code, status, text):
        self.mts = mts
        self.notify_type = notify_type
        self.message_id = message_id
        self.notify_info = notify_info
        self.code = code
        self.status = status
        self.text = text

    def is_success(self):
        """
        Check if the notification status was a success.

        @return bool: True if is success else False
        """
        if self.status == NotificationError.SUCCESS:
            return True
        return False

    @staticmethod
    def from_raw_notification(raw_notification):
        """
        Parse a raw notification object into an Order object

        @return Notification
        """
        mts = raw_notification[NotificationModal.MTS]
        notify_type = raw_notification[NotificationModal.TYPE]
        message_id = raw_notification[NotificationModal.MESSAGE_ID]
        notify_info = raw_notification[NotificationModal.NOTIFY_INFO]
        code = raw_notification[NotificationModal.CODE]
        status = raw_notification[NotificationModal.STATUS]
        text = raw_notification[NotificationModal.TEXT]

        basic = Notification(mts, notify_type, message_id, notify_info, code,
                             status, text)
        # if failure notification then just return as is
        if not basic.is_success():
            return basic
        # parse additional notification data
        if basic.notify_type == NotificationTypes.ORDER_NEW_REQ:
            basic.notify_info = Order.from_raw_order_snapshot(basic.notify_info)
        elif basic.notify_type == NotificationTypes.ORDER_CANCELED_REQ:
            basic.notify_info = Order.from_raw_order(basic.notify_info)
        elif basic.notify_type == NotificationTypes.ORDER_UPDATED_REQ:
            basic.notify_info = Order.from_raw_order(basic.notify_info)
        elif basic.notify_type == NotificationTypes.FUNDING_OFFER_NEW:
            basic.notify_info = FundingOffer.from_raw_offer(basic.notify_info)
        elif basic.notify_type == NotificationTypes.FUNDING_OFFER_CANCEL:
            basic.notify_info = FundingOffer.from_raw_offer(basic.notify_info)
        elif basic.notify_type == NotificationTypes.ACCOUNT_TRANSFER:
            basic.notify_info = Transfer.from_raw_transfer(basic.notify_info)
        elif basic.notify_type == NotificationTypes.ACCOUNT_DEPOSIT:
            basic.notify_info = DepositAddress.from_raw_deposit_address(basic.notify_info)
        elif basic.notify_type == NotificationTypes.ACCOUNT_WITHDRAW_REQ:
            basic.notify_info = Withdraw.from_raw_withdraw(basic.notify_info)
        return basic

    def __str__(self):
        """
        Allow us to print the Notification object in a pretty format
        """
        text = "Notification <'{}' ({}) - {} notify_info={}>"
        return text.format(self.notify_type, self.status, self.text, self.notify_info)
