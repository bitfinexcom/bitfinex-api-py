"""
This module contains a group of different models which
are used to define data types
"""

from .order import Order
from .trade import Trade
from .order_book import OrderBook
from .subscription import Subscription
from .wallet import Wallet
from .position import Position
from .funding_loan import FundingLoan
from .funding_offer import FundingOffer
from .funding_credit import FundingCredit
from .notification import Notification
from .transfer import Transfer
from .deposit_address import DepositAddress
from .withdraw import Withdraw
from .ticker import Ticker
from .funding_ticker import FundingTicker

NAME = 'models'
