"""
This module contains the BFX rest client data types
"""

import asyncio
import aiohttp
import time
import json

from ..utils.custom_logger import CustomLogger
from ..utils.auth import generate_auth_headers, calculate_order_flags, gen_unique_cid
from ..models import Wallet, Order, Position, Trade, FundingLoan, FundingOffer
from ..models import FundingCredit, Notification


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

    async def get_seed_candles(self, symbol, tf='1m'):
        """
        Used by the honey framework, this function gets the last 4k candles.
        """
        endpoint = 'candles/trade:{}:{}/hist?limit=5000&_bfx=1'.format(tf, symbol)
        time_difference = (1000 * 60) * 5000
        # get now to the nearest min
        now = int(round((time.time() // 60 * 60) * 1000))
        task_batch = []
        for x in range(0, 10):
            start = x * time_difference
            end = now - (x * time_difference) - time_difference
            e2 = endpoint + '&start={}&end={}'.format(start, end)
            task_batch += [asyncio.ensure_future(self.fetch(e2))]
        self.logger.info("Downloading seed candles from Bitfinex...")
        # call all fetch requests async
        done, _ = await asyncio.wait(*[task_batch])
        candles = []
        for task in done:
            candles += task.result()
        candles.sort(key=lambda x: x[0], reverse=True)
        self.logger.info("Downloaded {} candles.".format(len(candles)))
        return candles

    async def get_public_candles(self, symbol, start, end, section='hist',
                                 tf='1m', limit="100", sort=-1):
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

    async def get_public_trades(self, symbol, start, end, limit="100", sort=-1):
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
        return trades

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
        return [Wallet(*rw[:4]) for rw in raw_wallets]

    async def get_active_orders(self, symbol):
        """
        Get all of the active orders associated with API_KEY - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @return Array <models.Order>
        """
        endpoint = "auth/r/orders/{}".format(symbol)
        raw_orders = await self.post(endpoint)
        return [Order.from_raw_order(ro) for ro in raw_orders]

    async def get_order_history(self, symbol, start, end, limit=25, sort=-1):
        """
        Get all of the orders between the start and end period associated with API_KEY
        - Requires authentication.

        # Attributes
        @param symbol string: pair symbol i.e tBTCUSD
        @param start int: millisecond start time
        @param end int: millisecond end time
        @param limit int: max number of items in response
        @return Array <models.Order>
        """
        endpoint = "auth/r/orders/{}/hist".format(symbol)
        params = "?start={}&end={}&limit={}&sort={}".format(
            start, end, limit, sort)
        raw_orders = await self.post(endpoint, params=params)
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

    async def get_trades(self, symbol, start, end, limit=25):
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
        endpoint = "auth/r/trades/{}/hist".format(symbol)
        params = "?start={}&end={}&limit={}".format(start, end, limit)
        raw_trades = await self.post(endpoint, params=params)
        return [Trade.from_raw_rest_trade(rt) for rt in raw_trades]

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
        raw_notification = await self.post(endpoint,  { 'id': fundingId })
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
        raw_transfer = await self.post(endpoint,  payload)
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
        raw_notification = await self.post(endpoint, { 'id': orderId })
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
            payload['time_in_force'] = str(time_in_force)
        if leverage != None:
            payload["lev"] = str(leverage)
        flags = calculate_order_flags(
            hidden, close, reduce_only, post_only, False)
        payload['flags'] = flags
        endpoint = "auth/w/order/update"
        raw_notification = await self.post(endpoint, payload)
        return Notification.from_raw_notification(raw_notification)


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
