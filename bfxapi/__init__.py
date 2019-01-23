"""
This module is used to interact with the bitfinex api
"""

from .client import Client
from .models import (Order, Trade, OrderBook, Subscription, Wallet,
                     Position, FundingLoan, FundingOffer, FundingCredit)
from .websockets.GenericWebsocket import GenericWebsocket
from .utils.Decimal import Decimal

NAME = 'bfxapi'
