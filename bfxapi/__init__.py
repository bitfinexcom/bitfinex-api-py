"""
This module is used to interact with the bitfinex api
"""

from .version import __version__
from .client import Client
from .models import (Order, Trade, OrderBook, Subscription, Wallet,
                     Position, FundingLoan, FundingOffer, FundingCredit)
from .websockets.GenericWebsocket import GenericWebsocket, Socket
from .websockets.BfxWebsocket import BfxWebsocket
from .utils.Decimal import Decimal

NAME = 'bfxapi'
