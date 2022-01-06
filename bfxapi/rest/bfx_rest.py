"""
This module contains the BFX rest client data types
"""

import asyncio
import aiohttp
import time
import json
import datetime

from ..utils.custom_logger import CustomLogger
from ..utils.auth import generate_auth_headers, calculate_order_flags, gen_unique_cid
from ..models import Wallet, Order, Position, Trade, FundingLoan, FundingOffer, FundingTrade, MarginInfoBase, MarginInfo
from ..models import FundingCredit, Notification, Ledger


class BfxRest:
    """
    BFX rest interface contains functions which are used to interact with both the public
    and private Bitfinex http api's.
    To use the private api you have to set the API_KEY and API_SECRET variables to your
    api key.
    """

    def __init__(self, API_KEY, API_SECRET, host='https://api-pub.bitfinex.com/v2', loop=None,
                 logLevel='INFO', parse_float=float, *args, **kwargs):
        self.loop = loop or asyncio.get_event_loop()
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.host = host
        # this value can also be set to bfxapi.decimal for much higher precision
        self.parse_float = parse_float
        self.logger = CustomLogger('BfxRest', logLevel=logLevel)

    async def fetch(self, endpoint, params=""):
        """
        Send a GET request to the bitfinex api

        @return reponse
        """
        url = '{}/{}{}'.format(self.host, endpoint, params)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()
                if resp.status != 200:
                    raise Exception('GET {} failed with status {} - {}'
                                    .format(url, resp.status, text))
                parsed = json.loads(text, parse_float=self.parse_float)
                return parsed

    async def post(self, endpoint, data={}, params=""):
        """
        Send a pre-signed POST request to the bitfinex api

        @return response
        """
        url = '{}/{}'.format(self.host, endpoint)
        sData = json.dumps(data)
        headers = generate_auth_headers(
            self.API_KEY, self.API_SECRET, endpoint, sData)
        headers["content-type"] = "application/json"
        async with aiohttp.ClientSession() as session:
            async with session.post(url + params, headers=headers, data=sData) as resp:
                text = await resp.text()
                if resp.status < 200 or resp.status > 299:
                    raise Exception('POST {} failed with status {} - {}'
                                    .format(url, resp.status, text))
                parsed = json.loads(text, parse_float=self.parse_float)
                return parsed

    ##################################################
    #                  Public Data                   #
    ##################################################

    async def get_seed_candles(self, symbol, tf='1m', start=None, end=None, limit=10000, sort=0):
        """
        Get all of the seed candles between the start and end period.
        # Attributes
        @param symbol symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param tf int: timeframe inbetween candles i.e 1m (min), ..., 1D (day),
                      ... 1M (month)
        @param limit int: max number of items in response (max. 10000)
        @param sort int: if = 1 it sorts results returned with old > new
        @return Array [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ]
        """

        if not start and not end:
            start = 0
            end = int(round((time.time() // 60 * 60) * 1000))

        endpoint = f'candles/trade:{tf}:{symbol}/hist?limit={limit}&start={start}&end={end}&sort={sort}'
        self.logger.info("Downloading seed candles from Bitfinex...")
        candles = await self.fetch(endpoint)
        self.logger.info("Downloaded {} candles.".format(len(candles)))
        return candles

    async def get_public_candles(self, symbol, start, end, section='hist',
                                 tf='1m', limit=100, sort=-1):
        """
        Get all of the public candles between the start and end period.

        # Attributes
        @param symbol symbol string: pair symbol i.e tBTCUSD
        @param secton string: available values: "last", "hist"
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @param tf int: timeframe inbetween candles i.e 1m (min), ..., 1D (day), 
                      ... 1M (month)
        @param sort int: if = 1 it sorts results returned with old > new
        @return Array [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ]
        """
        endpoint = "candles/trade:{}:{}/{}".format(tf, symbol, section)
        params = "?start={}&end={}&limit={}&sort={}".format(
            start, end, limit, sort)
        candles = await self.fetch(endpoint, params=params)
        return candles

    async def get_public_trades(self, symbol, start, end, limit=100, sort=-1):
        """
        Get all of the public trades between the start and end period.

        # Attributes
        @param symbol symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array [ ID, MTS, AMOUNT, RATE, PERIOD? ]
        """
        endpoint = "trades/{}/hist".format(symbol)
        params = "?start={}&end={}&limit={}&sort={}".format(
            start, end, limit, sort)
        trades = await self.fetch(endpoint, params=params)
        return sorted(trades, key=lambda x: (x[1], x[0]), reverse=True if sort == 1 else False)

    async def get_public_books(self, symbol, precision="P0", length=25):
        """
        Get the public orderbook for a given symbol.

        # Attributes
        @param symbol symbol string: pair symbol i.e tBTCUSD
        @param precision string: level of price aggregation (P0, P1, P2, P3, P4, R0)
        @param length int: number of price points ("25", "100")
        @return Array [ PRICE, COUNT, AMOUNT ]
        """
        endpoint = "book/{}/{}".format(symbol, precision)
        params = "?len={}".format(length)
        books = await self.fetch(endpoint, params)
        return books

    async def get_public_ticker(self, symbol):
        """
        Get tickers for the given symbol. Tickers shows you the current best bid and ask,
        as well as the last trade price.

        # Attributes
        @param symbols symbol string: pair symbol i.e tBTCUSD
        @return Array [ SYMBOL, BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE,
          DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW ]
        """
        endpoint = "ticker/{}".format(symbol)
        ticker = await self.fetch(endpoint)
        return ticker

    async def get_public_tickers(self, symbols):
        """
        Get tickers for the given symbols. Tickers shows you the current best bid and ask,
        as well as the last trade price.

        # Attributes
        @param symbols Array<string>: array of symbols i.e [tBTCUSD, tETHUSD]
        @return Array [ SYMBOL, BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE,  DAILY_CHANGE_PERC,
          LAST_PRICE, VOLUME, HIGH, LOW ]
        """
        endpoint = "tickers/?symbols={}".format(','.join(symbols))
        ticker = await self.fetch(endpoint)
        return ticker

    async def get_public_tickers_history(self, symbols):
        """
        History of recent tickers.
        Provides historic data of the best bid and ask at a 10-second interval.

        # Attributes
        @param symbols Array<string>: array of symbols i.e [tBTCUSD, tETHUSD]
        @return Array [[ SYMBOL, BID, PLACEHOLDER, ASK, PLACEHOLDER, PLACEHOLDER,
        PLACEHOLDER, PLACEHOLDER, PLACEHOLDER, PLACEHOLDER, PLACEHOLDER, PLACEHOLDER, MTS ], ...]
        """
        endpoint = "tickers/hist?symbols={}".format(','.join(symbols))
        ticker = await self.fetch(endpoint)
        return ticker

    async def get_derivative_status(self, symbol):
        """
        Gets platform information for derivative symbol.

        # Attributes
        @param derivativeSymbol string: i.e tBTCF0:USTF0
        @return [KEY/SYMBOL, MTS, PLACEHOLDER, DERIV_PRICE, SPOT_PRICE, PLACEHOLDER, INSURANCE_FUND_BALANCE4,
            PLACEHOLDER, PLACEHOLDER, FUNDING_ACCRUED, FUNDING_STEP, PLACEHOLDER]
        """
        statuses = await self.get_derivative_statuses([symbol])
        if len(statuses) > 0:
            return statuses[0]
        return []

    async def get_derivative_statuses(self, symbols):
        """
        Gets platform information for a collection of derivative symbols.

        # Attributes
        @param derivativeSymbols Array<string>: array of symbols i.e [tBTCF0:USTF0 ...] or ["ALL"]
        @return [KEY/SYMBOL, MTS, PLACEHOLDER, DERIV_PRICE, SPOT_PRICE, PLACEHOLDER, INSURANCE_FUND_BALANCE4,
            PLACEHOLDER, PLACEHOLDER, FUNDING_ACCRUED, FUNDING_STEP, PLACEHOLDER]
        """
        endpoint = "status/deriv?keys={}".format(','.join(symbols))
        status = await self.fetch(endpoint)
        return status

    async def get_public_pulse_hist(self, end=None, limit=25):
        """
        View the latest pulse messages. You can specify an end timestamp to view older messages.

        # Attributes
        @param end int: millisecond end time
        @param limit int: max number of items in response (MAX: 100)
        @return Array [ PID, MTS, _PLACEHOLDER, PUID, _PLACEHOLDER, TITLE, CONTENT,
            _PLACEHOLDER, _PLACEHOLDER, IS_PIN, IS_PUBLIC, COMMENTS_DISABLED, TAGS,
            META, LIKES, _PLACEHOLDER, _PLACEHOLDER, [ PUID, MTS, _PLACEHOLDER,
            NICKNAME, PLACEHOLDER, PICTURE, TEXT, _PLACEHOLDER, _PLACEHOLDER, TWITTER_HANDLE,
            _PLACEHOLDER, FOLLOWERS, FOLLOWING, _PLACEHOLDER, _PLACEHOLDER, _PLACEHOLDER,
            TIPPING_STATUS ] ], COMMENTS, _PLACEHOLDER, _PLACEHOLDER ]
        """
        endpoint = f"pulse/hist?limit={limit}"
        if end:
            endpoint += f'&end={end}'
        hist = await self.fetch(endpoint)
        return hist

    async def get_public_pulse_profile(self, nickname='Bitfinex'):
        """
        This endpoint shows details for a specific Pulse profile

        # Attributes
        @param nickname string
        @return Array [ PUID, MTS, _PLACEHOLDER, NICKNAME, _PLACEHOLDER, PICTURE,
        TEXT, _PLACEHOLDER, _PLACEHOLDER, TWITTER_HANDLE, _PLACEHOLDER, FOLLOWERS,
        FOLLOWING, _PLACEHOLDER, _PLACEHOLDER, _PLACEHOLDER, TIPPING_STATUS]
        """
        endpoint = f"pulse/profile/{nickname}"
        profile = await self.fetch(endpoint)
        return profile

    async def get_market_average_price(self, symbol, amount=None, period=None, rate_limit=None):
        """
        Calculate the average execution price for Trading or rate for Margin funding.

        # Attributes
        @param symbol str: the symbol you want information about
        @param amount str: amount. Positive for buy, negative for sell
        @param period int: maximum period for Margin Funding
        @param rate_limit string: limit rate/price (ex. "1000.5")

        @return Array
        For exchange trading
        [PRICE_AVG, AMOUNT]

        For funding
        [RATE_AVG, AMOUNT]
        """
        endpoint = f"calc/trade/avg"
        payload = {
            "symbol": symbol,
            "amount": amount,
            "period": period,
            "rate_limit": rate_limit
        }
        message = await self.post(endpoint, payload)
        return message

    async def get_foreign_exchange_rate(self, ccy1, ccy2):
        """
        Calculate the average execution price for Trading or rate for Margin funding.

        # Attributes
        @param ccy1 str: base currency
        @param ccy2 str: quote currency

        @return Array [ CURRENT_RATE ]
        """
        endpoint = f"calc/fx"
        payload = {
            "ccy1": ccy1,
            "ccy2": ccy2
        }
        message = await self.post(endpoint, payload)
        return message

    async def get_public_stats(self, key, size, symbol, section, side=None,
                               sort=None, start=None, end=None, limit=None):
        """
        The Stats endpoint provides various statistics on a specified trading pair or funding currency.

        # Attributes
        @param key str
        Available values -> "funding.size", "credits.size", "credits.size.sym",
        "pos.size", "vol.1d", "vol.7d", "vol.30d", "vwap"

        @param size str
        Available values -> "30m", "1d", '1m'

        @param symbol str: the symbol you want information about
        (e.g. tBTCUSD, tETHUSD, fUSD, fBTC)

        @param section str
        Available values -> "last", "hist"

        @param side str: only for non-funding queries
        Available values -> "long", "short"

        @param sort int: if = 1 it sorts results returned with old > new

        @param start str: millisecond start time

        @param end str: millisecond end time

        @param limit int: number of records (max 10000)

        @return
        Array [MTS, VALUE] with Section = "last"
        Array [[MTS, VALUE], ...] with Section = "hist"
        """
        if key != 'funding.size' and not side:
            raise Exception('side is compulsory for non funding queries')
        endpoint = f"stats1/{key}:{size}:{symbol}"
        if side:
            endpoint += f":{side}"
        if section:
            endpoint += f"/{section}"
        endpoint += '?'
        if sort:
            endpoint += f"sort={sort}&"
        if start:
            endpoint += f"start={start}&"
        if end:
            endpoint += f"end={end}&"
        if limit:
            endpoint += f"limit={limit}"
        message = await self.fetch(endpoint)
        return message


    async def get_public_funding_stats(self, symbol, start=None, end=None, limit=100):
        """
        Get a list of the most recent funding data for the given currency
        (FRR, average period, total amount provided, total amount used)

        # Attributes
        @param limit int: number of results (max 250)
        @param start str: millisecond start time
        @param end str: millisecond end time

        @return Array
        [[ TIMESTAMP,  PLACEHOLDER, PLACEHOLDER, FRR, AVG_PERIOD, PLACEHOLDER,
        PLACEHOLDER, FUNDING_AMOUNT, FUNDING_AMOUNT_USED ], ...]
        """
        endpoint = f"funding/stats/{symbol}/hist?start={start}&end={end}&limit={limit}"
        stats = await self.fetch(endpoint)
        return stats

    async def get_conf_list_pair_exchange(self):
        """
        Get list of available exchange pairs
        # Attributes
        @return Array [ SYMBOL ]
        """
        endpoint = "conf/pub:list:pair:exchange"
        pairs = await self.fetch(endpoint)
        return pairs

    ##################################################
    #               Authenticated Data               #
    ##################################################

    async def get_wallets(self):
        """
        Get all wallets on account associated with API_KEY - Requires authentication.

        @return Array <models.Wallet>
        """
        endpoint = "auth/r/wallets"
        raw_wallets = await self.post(endpoint)
        return [Wallet(*rw[:5]) for rw in raw_wallets]

    async def get_margin_info(self, symbol='base'):
        """
        Get account margin information (like P/L, Swaps, Margin Balance, Tradable Balance and others).
        Use different keys (base, SYMBOL, sym_all) to retrieve different kinds of data.

        @return Array
        """
        endpoint = f"auth/r/info/margin/{symbol}"
        raw_margin_info = await self.post(endpoint)
        if symbol == 'base':
            return MarginInfoBase.from_raw_margin_info(raw_margin_info)
        elif symbol == 'sym_all':
            return [MarginInfo.from_raw_margin_info(record) for record in raw_margin_info]
        else:
            return MarginInfo.from_raw_margin_info(raw_margin_info)

    async def get_active_orders(self, symbol=None):
        """
        Get all of the active orders associated with API_KEY - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @return Array <models.Order>
        """
        if symbol is None:
            endpoint = "auth/r/orders"
        else:
            endpoint = "auth/r/orders/{}".format(symbol)
        raw_orders = await self.post(endpoint)
        return [Order.from_raw_order(ro) for ro in raw_orders]

    async def get_order_history(self, symbol=None, start=None, end=None, limit=2500, sort=-1, ids=None):
        """
        Get all of the orders between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @param ids list of int: allows you to retrieve specific orders by order ID (ids: [ID1, ID2, ID3])
        @return Array <models.Order>
        """
        endpoint = "auth/r/orders/{}/hist".format(symbol) if symbol else "auth/r/orders/hist"
        payload = {}
        if start:
            payload['start'] = start
        if end:
            payload['end'] = end
        if limit:
            payload['limit'] = limit
        if sort:
            payload['sort'] = sort
        if ids:
            payload['id'] = ids
        raw_orders = await self.post(endpoint, payload)
        return [Order.from_raw_order(ro) for ro in raw_orders]

    async def get_active_position(self):
        """
        Get all of the active position associated with API_KEY - Requires authentication.

        @return Array <models.Position>
        """
        endpoint = "auth/r/positions"
        raw_positions = await self.post(endpoint)
        return [Position.from_raw_rest_position(rp) for rp in raw_positions]

    async def get_order_trades(self, symbol, order_id):
        """
        Get all of the trades that have been generated by the given order associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param order_id string: id of the order
        @return Array <models.Trade>
        """
        endpoint = "auth/r/order/{}:{}/trades".format(symbol, order_id)
        raw_trades = await self.post(endpoint)
        return [Trade.from_raw_rest_trade(rt) for rt in raw_trades]

    async def get_trades(self, symbol=None, start=None, end=None, limit=25):
        """
        Get all of the trades between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array <models.Trade>
        """
        endpoint = "auth/r/trades/{}/hist".format(symbol) if symbol else "auth/r/trades/hist"
        params = "?start={}&end={}&limit={}".format(start, end, limit)
        raw_trades = await self.post(endpoint, params=params)
        return [Trade.from_raw_rest_trade(rt) for rt in raw_trades]

    async def get_funding_trades(self, symbol, start, end, limit=25):
        """
        Get all of the funding trades between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e fUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array <models.FundingTrade>
        """
        endpoint = "auth/r/funding/trades/{}/hist".format(symbol)
        raw_trades = await self.post(endpoint)
        return [FundingTrade.from_raw_rest_trade(rt) for rt in raw_trades]

    async def get_funding_offers(self, symbol):
        """
        Get all of the funding offers associated with API_KEY - Requires authentication.

        @return Array <models.FundingOffer>
        """
        endpoint = "auth/r/funding/offers/{}".format(symbol)
        offers = await self.post(endpoint)
        return [FundingOffer.from_raw_offer(o) for o in offers]

    async def get_funding_offer_history(self, symbol, start, end, limit=25):
        """
        Get all of the funding offers between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array <models.FundingOffer>
        """
        endpoint = "auth/r/funding/offers/{}/hist".format(symbol)
        params = "?start={}&end={}&limit={}".format(start, end, limit)
        offers = await self.post(endpoint, params=params)
        return [FundingOffer.from_raw_offer(o) for o in offers]

    async def get_funding_loans(self, symbol):
        """
        Get all of the funding loans associated with API_KEY - Requires authentication.

        @return Array <models.FundingLoan>
        """
        endpoint = "auth/r/funding/loans/{}".format(symbol)
        loans = await self.post(endpoint)
        return [FundingLoan.from_raw_loan(o) for o in loans]

    async def get_funding_loan_history(self, symbol, start, end, limit=25):
        """
        Get all of the funding loans between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array <models.FundingLoan>
        """
        endpoint = "auth/r/funding/loans/{}/hist".format(symbol)
        params = "?start={}&end={}&limit={}".format(start, end, limit)
        loans = await self.post(endpoint, params=params)
        return [FundingLoan.from_raw_loan(o) for o in loans]

    async def get_funding_credits(self, symbol):
        endpoint = "auth/r/funding/credits/{}".format(symbol)
        credits = await self.post(endpoint)
        return [FundingCredit.from_raw_credit(c) for c in credits]

    async def get_funding_credit_history(self, symbol, start, end, limit=25):
        """
        Get all of the funding credits between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array <models.FundingCredit>
        """
        endpoint = "auth/r/funding/credits/{}/hist".format(symbol)
        params = "?start={}&end={}&limit={}".format(start, end, limit)
        credits = await self.post(endpoint, params=params)
        return [FundingCredit.from_raw_credit(c) for c in credits]

    async def get_ledgers(self, symbol, start, end, limit=25, category=None):
        """
        Get all ledgers on account associated with API_KEY - Requires authentication.

        You can emit the symbol param in order to receive ledger entries for all symbols.
        See category filters here: https://docs.bitfinex.com/reference#rest-auth-ledgers

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD - can be omitted to receive all entries
        @param start int: start of window
        @param end int: end of window
        @param limit int: max number of entries
        @param category int: filter category to receive specific ledger entries

        @return Array <models.Ledger>
        """
        endpoint = ("auth/r/ledgers/{}/hist".format(symbol)
                    if symbol else "auth/r/ledgers/hist")
        params = "?start={}&end={}&limit={}".format(start, end, limit)
        if category:
            payload = {"category": category}
            raw_ledgers = await self.post(endpoint, payload, params=params)
        else:
            raw_ledgers = await self.post(endpoint, params=params)
        return [Ledger.from_raw_ledger(rl) for rl in raw_ledgers]

    async def submit_funding_offer(self, symbol, amount, rate, period,
                                   funding_type=FundingOffer.Type.LIMIT, hidden=False):
        """
        Submits a new funding offer

        # Attributes
        @param symbol string: pair symbol i.e fUSD
        @param amount float: funding size
        @param rate float: percentage rate to charge per a day
        @param period int: number of days for funding to remain active once accepted
        """
        payload = {
            "type": funding_type,
            "symbol": symbol,
            "amount": str(amount),
            "rate": str(rate),
            "period": period,
        }
        # calculate and add flags
        flags = calculate_order_flags(hidden, None, None, None, None)
        payload['flags'] = flags
        endpoint = "auth/w/funding/offer/submit"
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)

    async def submit_cancel_funding_offer(self, fundingId):
        """
        Cancel a funding offer

        # Attributes
        @param fundingId int: the id of the funding offer
        """
        endpoint = "auth/w/funding/offer/cancel"
        raw_notification = await self.post(endpoint, {'id': fundingId})
        return Notification.from_raw_notification(raw_notification)

    async def submit_cancel_all_funding_offer(self, currency):
        """
        Cancel all funding offers at once

        # Attributes
        @param currency str: currency for which to cancel all offers (USD, BTC, UST ...)
        """
        endpoint = "auth/w/funding/offer/cancel/all"
        raw_notification = await self.post(endpoint, {'currency': currency})
        return Notification.from_raw_notification(raw_notification)

    async def keep_funding(self, type, id):
        """
        Toggle to keep funding taken. Specify loan for unused funding and credit for used funding.

        # Attributes
        @param type string: funding type ('credit' or 'loan')
        @param id int: loan or credit identifier
        """
        endpoint = "auth/w/funding/keep"
        payload = {
            "type": type,
            "id": id
        }
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)

    async def submit_wallet_transfer(self, from_wallet, to_wallet, from_currency, to_currency, amount):
        """
        Transfer funds between wallets

        # Attributes
        @param from_wallet string: wallet name to transfer from i.e margin, exchange
        @param to_wallet string: wallet name to transfer to i.e margin, exchange
        @param from_currency string: currency symbol to tranfer from i.e BTC, USD
        @param to_currency string: currency symbol to transfer to i.e BTC, USD
        @param amount float: amount of funds to transfer
        """
        endpoint = "auth/w/transfer"
        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "currency": from_currency,
            "currency_to": to_currency,
            "amount": str(amount),
        }
        raw_transfer = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_transfer)

    async def get_wallet_deposit_address(self, wallet, method, renew=0):
        """
        Get the deposit address for the given wallet and protocol

        # Attributes
        @param wallet string: wallet name i.e margin, exchange
        @param method string: transfer protocol i.e bitcoin
        """
        endpoint = "auth/w/deposit/address"
        payload = {
            "wallet": wallet,
            "method": method,
            "op_renew": renew,
        }
        raw_deposit = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_deposit)

    async def create_wallet_deposit_address(self, wallet, method):
        """
        Creates a new deposit address for the given wallet and protocol.
        Previously generated addresses remain linked.

        # Attributes
        @param wallet string: wallet name i.e margin, exchange
        @param method string: transfer protocol i.e bitcoin
        """
        return await self.get_wallet_deposit_address(wallet, method, renew=1)

    async def submit_wallet_withdraw(self, wallet, method, amount, address):
        """
        Submits a request to withdraw crypto funds to an external wallet.

        # Attributes
        @param wallet string: wallet name i.e margin, exchange
        @param method string: transfer protocol i.e bitcoin
        @param amount float: amount of funds to withdraw
        @param address string: external address to withdraw to
        """
        endpoint = "auth/w/withdraw"
        payload = {
            "wallet": wallet,
            "method": method,
            "amount": str(amount),
            "address": str(address)
        }
        raw_deposit = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_deposit)

    # async def submit_close_funding(self, id, type):
    #     """
    #     `/v2/auth/w/funding/close` (params: `id`, `type` (credit|loan))
    #     """
    #     pass

    # async def submit_auto_funding(self, ):
    #     """
    #     `/v2/auth/w/funding/auto` (params: `status` (1|0), `currency`, `amount`, `rate`, `period`)
    #     (`rate === 0` means `FRR`)
    #     """
    #     pass

    ##################################################
    #                    Orders                      #
    ##################################################

    async def submit_order(self, symbol, price, amount, market_type=Order.Type.LIMIT,
                           hidden=False, price_trailing=None, price_aux_limit=None,
                           oco_stop_price=None, close=False, reduce_only=False,
                           post_only=False, oco=False, aff_code=None, time_in_force=None,
                           leverage=None, gid=None):
        """
        Submit a new order

        # Attributes
        @param gid: assign the order to a group identifier
        @param symbol: the name of the symbol i.e 'tBTCUSD
        @param price: the price you want to buy/sell at (must be positive)
        @param amount: order size: how much you want to buy/sell,
          a negative amount indicates a sell order and positive a buy order
        @param market_type	Order.Type: please see Order.Type enum
          amount	decimal string	Positive for buy, Negative for sell
        @param hidden: if True, order should be hidden from orderbooks
        @param price_trailing:	decimal trailing price
        @param price_aux_limit:	decimal	auxiliary Limit price (only for STOP LIMIT)
        @param oco_stop_price: set the oco stop price (requires oco = True)
        @param close: if True, close position if position present
        @param reduce_only: if True, ensures that the executed order does not flip the opened position
        @param post_only: if True, ensures the limit order will be added to the order book and not
          match with a pre-existing order
        @param oco: cancels other order option allows you to place a pair of orders stipulating
          that if one order is executed fully or partially, then the other is automatically canceled
        @param aff_code: bitfinex affiliate code
        @param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
        @param leverage: the amount of leverage to apply to the order as an integer
        """
        cid = gen_unique_cid()
        payload = {
            "cid": cid,
            "type": str(market_type),
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "meta": {}
        }
        # calculate and add flags
        flags = calculate_order_flags(hidden, close, reduce_only, post_only, oco)
        payload['flags'] = flags
        # add extra parameters
        if price_trailing != None:
            payload['price_trailing'] = price_trailing
        if price_aux_limit != None:
            payload['price_aux_limit'] = price_aux_limit
        if oco_stop_price != None:
            payload['price_oco_stop'] = str(oco_stop_price)
        if time_in_force != None:
            payload['tif'] = time_in_force
        if gid != None:
            payload['gid'] = gid
        if leverage != None:
            payload['lev'] = str(leverage)
        if aff_code != None:
            payload['meta']['aff_code'] = str(aff_code)
        endpoint = "auth/w/order/submit"
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)

    async def submit_cancel_order(self, orderId):
        """
        Cancel an existing open order

        # Attributes
        @param orderId: the id of the order that you want to update
        """
        endpoint = "auth/w/order/cancel"
        raw_notification = await self.post(endpoint, {'id': orderId})
        return Notification.from_raw_notification(raw_notification)

    async def submit_cancel_order_multi(self, ids=None, cids=None, gids=None, all=None):
        """
        Cancel multiple orders simultaneously. Orders can be canceled based on the Order ID,
        the combination of Client Order ID and Client Order Date, or the Group Order ID.
        Alternatively, the body param 'all' can be used with a value of 1 to cancel all orders.

        # Attributes
        @param id array of int: orders ids
        [1234, 1235, ...]

        @param cids array of arrays: client orders ids
        [[234, "2016-12-05"], ...]

        @param gids array of int: group orders id
        [11, ...]

        @param all int: cancel all open orders if value is set to 1
        """
        endpoint = "auth/w/order/cancel/multi"
        payload = {}
        if ids != None:
            payload["id"] = ids
        if cids != None:
            payload["cid"] = cids
        if gids != None:
            payload["gid"] = gids
        if all != None:
            payload["all"] = all
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)

    async def submit_update_order(self, orderId, price=None, amount=None, delta=None, price_aux_limit=None,
                                  price_trailing=None, hidden=False, close=False, reduce_only=False,
                                  post_only=False, time_in_force=None, leverage=None):
        """
        Update an existing order

        # Attributes
        @param orderId: the id of the order that you want to update
        @param price: the price you want to buy/sell at (must be positive)
        @param amount: order size: how much you want to buy/sell,
          a negative amount indicates a sell order and positive a buy order
        @param delta:	change of amount
        @param price_trailing:	decimal trailing price
        @param price_aux_limit:	decimal	auxiliary Limit price (only for STOP LIMIT)
        @param hidden: if True, order should be hidden from orderbooks
        @param close: if True, close position if position present
        @param reduce_only: if True, ensures that the executed order does not flip the opened position
        @param post_only: if True, ensures the limit order will be added to the order book and not
          match with a pre-existing order
        @param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
        @param leverage: the amount of leverage to apply to the order as an integer
        """
        payload = {"id": orderId}
        if price != None:
            payload['price'] = str(price)
        if amount != None:
            payload['amount'] = str(amount)
        if delta != None:
            payload['delta'] = str(delta)
        if price_aux_limit != None:
            payload['price_aux_limit'] = str(price_aux_limit)
        if price_trailing != None:
            payload['price_trailing'] = str(price_trailing)
        if time_in_force != None:
            payload['tif'] = str(time_in_force)
        if leverage != None:
            payload["lev"] = str(leverage)
        flags = calculate_order_flags(
            hidden, close, reduce_only, post_only, False)
        payload['flags'] = flags
        endpoint = "auth/w/order/update"
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)

    async def submit_order_multi_op(self, orders):
        """
        Send Multiple order-related operations.
        Please note the sent object has only one property with a value
        of an array of arrays detailing each order operation.

        https://docs.bitfinex.com/reference#rest-auth-order-multi

        Expected orders ->
        [
            ["on", {  // Order Submit
                type: "EXCHANGE LIMIT",
                symbol: "tBTCUSD",
                price: "123.45",
                amount: "1.2345",
                flags: 0
        	}],
        	["oc", { ... }],
        	...
        ]

        @param type string
        Available values -> LIMIT, EXCHANGE LIMIT, MARKET, EXCHANGE MARKET,
        STOP, EXCHANGE STOP, STOP LIMIT, EXCHANGE STOP LIMIT, TRAILING STOP,
        EXCHANGE TRAILING STOP, FOK, EXCHANGE FOK, IOC, EXCHANGE IOC

        @param symbol string: symbol of order

        @param price string: price of order

        @param amount string: amount of order (positive for buy, negative for sell)

        @param flags int: (optional) see https://docs.bitfinex.com/v2/docs/flag-values

        @param lev int: set the leverage for a derivative order, supported
        by derivative symbol orders only. The value should be between 1 and
        100 inclusive. The field is optional, if omitted the default leverage value of 10 will be used.

        @param price_trailing string: the trailing price for a trailing stop order

        @param price_aux_limit string: auxiliary Limit price (for STOP LIMIT)

        @param price_oco_stop string: OCO stop price

        @param gid int: group order id

        @param tif string: Time-In-Force - datetime for automatic order cancellation (YYYY-MM-DD HH:MM:SS)

        @param id int: Order ID (can be retrieved by calling the Retrieve Orders endpoint)

        @param cid int: Client Order ID

        @param cid_date string: Client Order ID Date (YYYY-MM-DD)

        @param all int: cancel all open orders if value is set to 1
        """
        payload = {"ops": orders}
        endpoint = "auth/w/order/multi"
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)

    async def claim_position(self, position_id, amount):
        """
        The claim feature allows the use of funds you have in your Margin Wallet
        to settle a leveraged position as an exchange buy or sale

        # Attributes
        @param position_id: id of the position
        @param amount: amount to claim
        @return Array [ MTS, TYPE, MESSAGE_ID, null, [SYMBOL, POSITION_STATUS,
        AMOUNT, BASE_PRICE, MARGIN_FUNDING, MARGIN_FUNDING_TYPE, PLACEHOLDER,
        PLACEHOLDER, PLACEHOLDER, PLACEHOLDER, PLACEHOLDER, POSITION_ID, MTS_CREATE,
        MTS_UPDATE, PLACEHOLDER, POS_TYPE, PLACEHOLDER, COLLATERAL, MIN_COLLATERAL,
        META], CODE, STATUS, TEXT]
        """
        payload = {
            "id": position_id,
            "amount": f"{amount * -1}"
        }
        endpoint = "auth/w/position/claim"
        message = await self.post(endpoint, payload)
        return message

    async def get_auth_pulse_hist(self, is_public=None):
        """
        Allows you to retrieve your private pulse history or the public pulse history with an additional UID_LIKED field.

        # Attributes
        @param is_public int: allows you to receive the public pulse history with the UID_LIKED field
        @return Array [ PID, MTS, _PLACEHOLDER, PUID, _PLACEHOLDER, TITLE,
        CONTENT, _PLACEHOLDER, _PLACEHOLDER, IS_PIN, IS_PUBLIC, COMMENTS_DISABLED,
        TAGS, META,LIKES, UID_LIKED, _PLACEHOLDER, [ PUID, MTS, _PLACEHOLDER, NICKNAME,
        _PLACEHOLDER, PICTURE, TEXT, _PLACEHOLDER, _PLACEHOLDER, TWITTER_HANDLE, _PLACEHOLDER,
        FOLLOWERS, FOLLOWING, _PLACEHOLDER, _PLACEHOLDER, _PLACEHOLDER, TIPPING_STATUS ], COMMENTS,
        _PLACEHOLDER, _PLACEHOLDER ]
        """
        endpoint = f"auth/r/pulse/hist"
        if is_public:
            endpoint += f'?isPublic={is_public}'
        hist = await self.post(endpoint)
        return hist

    async def submit_pulse(self, title, content, parent=None, is_pin=False,
                        attachments=[], disable_comments=False, is_public=True):
        """
        Allows you to write Pulse messages

        # Attributes
        @param title str: title of the message (min 16, max 120 characters)
        @param content str: content of the message
        @param parent str: Pulse Message ID (PID) of parent post
        @param is_pin boolean: is message pinned?
        @param attachments list of str: base64 format
        @param disable_comments boolean: are comments disabled?
        @param is_public boolean: is a public message?
        @return Array [ PID, MTS, _PLACEHOLDER, PUID, _PLACEHOLDER, TITLE,
        CONTENT, _PLACEHOLDER, _PLACEHOLDER, IS_PIN, IS_PUBLIC, COMMENTS_DISABLED,
        TAGS // This inner array contains zero or more tag strings ATTACHMENTS, _PLACEHOLDER,
        LIKES, UID_LIKED, _PLACEHOLDER, [], ... ]
        """
        endpoint = f"auth/w/pulse/add"
        payload = {
            "title": title,
            "content": content,
            "isPin": 1 if is_pin else 0,
            "attachments": attachments,
            "disableComments": 1 if disable_comments else 0,
            "isPublic": 1 if is_public else 0
        }
        if parent:
            payload["parent"] = parent
        message = await self.post(endpoint, payload)
        return message

    async def submit_pulse_comment(self, title, content, parent, is_pin=False,
                        attachments=[], disable_comments=False, is_public=True):
        """
        Allows you to write a Pulse comment

        # Attributes
        @param title str: title of the message (min 16, max 120 characters)
        @param content str: content of the message
        @param parent str: Pulse Message ID (PID) of parent post
        @param is_pin boolean: is message pinned?
        @param attachments list of str: base64 format
        @param disable_comments boolean: are comments disabled?
        @param is_public boolean: is a public message?
        @return Array [ PID, MTS, _PLACEHOLDER, PUID, _PLACEHOLDER, TITLE,
        CONTENT, _PLACEHOLDER, _PLACEHOLDER, IS_PIN, IS_PUBLIC, COMMENTS_DISABLED,
        TAGS // This inner array contains zero or more tag strings ATTACHMENTS, _PLACEHOLDER,
        LIKES, UID_LIKED, _PLACEHOLDER, [], ... ]
        """
        endpoint = f"auth/w/pulse/add"
        payload = {
            "title": title,
            "content": content,
            "isPin": 1 if is_pin else 0,
            "attachments": attachments,
            "disableComments": 1 if disable_comments else 0,
            "isPublic": 1 if is_public else 0,
            "parent": parent
        }
        message = await self.post(endpoint, payload)
        return message

    async def delete_pulse(self, pid):
        """
        Allows you to delete your Pulse messages

        # Attributes
        @param pid str: ID of the pulse message that you want to delete
        @return Array [1] or [0]
        """
        endpoint = f"auth/w/pulse/del"
        payload = {
            'pid': pid
        }
        message = await self.post(endpoint, payload)
        return message

    async def generate_invoice(self, amount, wallet='exchange', currency='LNX'):
        """
        Generates a Lightning Network deposit invoice

        # Attributes
        @param wallet str: Select the wallet that will receive the invoice payment
        Currently only 'exchange' is available
        @param currency str: Select the currency for which you wish to generate an invoice
        Currently only LNX (Bitcoin Lightning Network) is available.
        @param amount str: Amount that you wish to deposit (in BTC; min 0.000001, max 0.02)

        @return Array [INVOICE_HASH, INVOICE, PLACEHOLDER, PLACEHOLDER, AMOUNT]

        If this is the first time you are generating an LNX invoice on your account,
        you will first need to create a deposit address. To do this, call
        self.get_wallet_deposit_address(method='LNX', wallet='exchange')
        """
        endpoint = f"auth/w/deposit/invoice"
        payload = {
            "wallet": wallet,
            "currency": currency,
            "amount": amount
        }
        message = await self.post(endpoint, payload)
        return message

    ##################################################
    #                   Derivatives                  #
    ##################################################

    async def set_derivative_collateral(self, symbol, collateral):
        """
        Update the amount of callateral used to back a derivative position.

        # Attributes
        @param symbol of the derivative i.e 'tBTCF0:USTF0'
        @param collateral: amount of collateral/value to apply to the open position
        """
        endpoint = 'auth/w/deriv/collateral/set'
        payload = {}
        payload['symbol'] = symbol
        payload['collateral'] = collateral
        return await self.post(endpoint, data=payload)

    ##################################################
    #                   Merchants                    #
    ##################################################

    async def submit_invoice(self, amount, currency, pay_currencies, order_id, webhook, redirect_url, customer_info_nationality,
                             customer_info_resid_country, customer_info_resid_city, customer_info_resid_zip_code,
                             customer_info_resid_street, customer_info_full_name, customer_info_email,
                             customer_info_resid_state=None, customer_info_resid_building_no=None, duration=None):
        """
        Submit an invoice for payment

        # Attributes
        @param amount str: Invoice amount in currency (From 0.1 USD to 1000 USD)
        @param currency str: Invoice currency, currently supported: USD
        @param pay_currencies list of str: Currencies in which invoice accepts the payments, supported values are BTC, ETH, UST-ETH, UST-TRX, UST-LBT, LNX, LBT
        @param order_id str: Reference order identifier in merchant's platform
        @param webhook str: The endpoint that will be called once the payment is completed/expired
        @param redirect_url str: Merchant redirect URL, this one is used in UI to redirect customer to merchant's site once the payment is completed/expired
        @param customer_info_nationality str: Customer's nationality, alpha2 code or full country name (alpha2 preffered)
        @param customer_info_resid_country str: Customer's residential country, alpha2 code or full country name (alpha2 preffered)
        @param customer_info_resid_city str: Customer's residential city/town
        @param customer_info_resid_zip_code str: Customer's residential zip code/postal code
        @param customer_info_resid_street str: Customer's residential street address
        @param customer_info_full_name str: Customer's full name
        @param customer_info_email str: Customer's email address
        @param customer_info_resid_state str: Optional, customer's residential state/province
        @param customer_info_resid_building_no str: Optional, customer's residential building number/name
        @param duration int: Optional, invoice expire time in seconds, minimal duration is 5 mins (300) and maximal duration is 24 hours (86400). Default value is 15 minutes
        """
        endpoint = 'auth/w/ext/pay/invoice/create'
        payload = {
            'amount': amount,
            'currency': currency,
            'payCurrencies': pay_currencies,
            'orderId': order_id,
            'webhook': webhook,
            'redirectUrl': redirect_url,
            'customerInfo': {
                'nationality': customer_info_nationality,
                'residCountry': customer_info_resid_country,
                'residCity': customer_info_resid_city,
                'residZipCode': customer_info_resid_zip_code,
                'residStreet': customer_info_resid_street,
                'fullName': customer_info_full_name,
                'email': customer_info_email
            },
            'duration': duration
        }

        if customer_info_resid_state:
            payload['customerInfo']['residState'] = customer_info_resid_state

        if customer_info_resid_building_no:
            payload['customerInfo']['residBuildingNo'] = customer_info_resid_building_no

        return await self.post(endpoint, data=payload)

    async def get_invoices(self, id=None, start=None, end=None, limit=10):
        """
        List submitted invoices

        # Attributes
        @param id str: Unique invoice identifier
        @param start int: Millisecond start time
        @param end int: Millisecond end time
        @param limit int: Millisecond start time
        """
        endpoint = 'auth/r/ext/pay/invoices'
        payload = {}

        if id:
            payload['id'] = id

        if start:
            payload['start'] = start

        if end:
            payload['end'] = end

        if limit:
            payload['limit'] = limit

        return await self.post(endpoint, data=payload)

    async def complete_invoice(self, id, pay_ccy, deposit_id=None, ledger_id=None):
        """
        Manually complete an invoice

        # Attributes
        @param id str: Unique invoice identifier
        @param pay_ccy str: Paid invoice currency, should be one of values under payCurrencies field on invoice
        @param deposit_id int: Movement/Deposit Id linked to invoice as payment
        @param ledger_id int: Ledger entry Id linked to invoice as payment, use either depositId or ledgerId
        """
        endpoint = 'auth/w/ext/pay/invoice/complete'
        payload = {
            'id': id,
            'payCcy': pay_ccy
        }

        if deposit_id:
            payload['depositId'] = deposit_id

        if ledger_id:
            payload['ledgerId'] = ledger_id

        return await self.post(endpoint, data=payload)

    async def get_unlinked_deposits(self, ccy, start=None, end=None):
        """
        Retrieve deposits that possibly could be linked to bitfinex pay invoices

        # Attributes
        @param ccy str: Pay currency to search deposits for, supported values are: BTC, ETH, UST-ETH, UST-TRX, UST-LBT, LNX, LBT
        @param start int: Millisecond start time
        @param end int: Millisecond end time
        """
        endpoint = 'auth/r/ext/pay/deposits/unlinked'
        payload = {
            'ccy': ccy
        }

        if start:
            payload['start'] = start

        if end:
            payload['end'] = end

        return await self.post(endpoint, data=payload)
