"""
This module is used to interact with the bitfinex api
"""

from .version import __version__
from .client import Client
from .models import (Order, Trade, OrderBook, Subscription, Wallet,
                     Position, FundingLoan, FundingOffer, FundingCredit)
from .websockets.generic_websocket import GenericWebsocket, Socket
from .websockets.bfx_websocket import BfxWebsocket
from .utils.decimal import Decimal

NAME = 'bfxapi'
