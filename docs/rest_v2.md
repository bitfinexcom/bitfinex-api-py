
# bfxapi

This module is used to interact with the bitfinex api


# bfxapi.client

This module exposes the core bitfinex clients which includes both
a websocket client and a rest interface client


## Client
```python
Client(self,
       API_KEY=None,
       API_SECRET=None,
       rest_host='https://api-pub.bitfinex.com/v2',
       ws_host='wss://api-pub.bitfinex.com/ws/2',
       create_event_emitter=None,
       logLevel='INFO',
       dead_man_switch=False,
       ws_capacity=25,
       channel_filter=[],
       *args,
       **kwargs)
```

The bfx client exposes rest and websocket objects


# BfxRest
```python
BfxRest(self,
        API_KEY,
        API_SECRET,
        host='https://api-pub.bitfinex.com/v2',
        loop=None,
        logLevel='INFO',
        parse_float=float,
        *args,
        **kwargs)
```

BFX rest interface contains functions which are used to interact with both the public
and private Bitfinex http api's.
To use the private api you have to set the API_KEY and API_SECRET variables to your
api key.


## fetch
```python
BfxRest.fetch(endpoint, params='')
```

Send a GET request to the bitfinex api

@return reponse


## post
```python
BfxRest.post(endpoint, data={}, params='')
```

Send a pre-signed POST request to the bitfinex api

@return response


## get_seed_candles
```python
BfxRest.get_seed_candles(symbol, tf='1m')
```

Used by the honey framework, this function gets the last 4k candles.


## get_public_candles
```python
BfxRest.get_public_candles(symbol,
                           start,
                           end,
                           section='hist',
                           tf='1m',
                           limit='100',
                           sort=-1)
```

Get all of the public candles between the start and end period.

__Attributes__

- `@param symbol symbol string`: pair symbol i.e tBTCUSD
- `@param secton string`: available values: "last", "hist"
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
- `@param tf int`: timeframe inbetween candles i.e 1m (min), ..., 1D (day),
              ... 1M (month)
- `@param sort int`: if = 1 it sorts results returned with old > new
@return Array [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ]


## get_public_trades
```python
BfxRest.get_public_trades(symbol, start, end, limit='100', sort=-1)
```

Get all of the public trades between the start and end period.

__Attributes__

- `@param symbol symbol string`: pair symbol i.e tBTCUSD
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
@return Array [ ID, MTS, AMOUNT, RATE, PERIOD? ]


## get_public_books
```python
BfxRest.get_public_books(symbol, precision='P0', length=25)
```

Get the public orderbook for a given symbol.

__Attributes__

- `@param symbol symbol string`: pair symbol i.e tBTCUSD
- `@param precision string`: level of price aggregation (P0, P1, P2, P3, P4, R0)
- `@param length int`: number of price points ("25", "100")
@return Array [ PRICE, COUNT, AMOUNT ]


## get_public_ticker
```python
BfxRest.get_public_ticker(symbol)
```

Get tickers for the given symbol. Tickers shows you the current best bid and ask,
as well as the last trade price.

__Attributes__

- `@param symbols symbol string`: pair symbol i.e tBTCUSD
@return Array [ SYMBOL, BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE,
  DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW ]


## get_public_tickers
```python
BfxRest.get_public_tickers(symbols)
```

Get tickers for the given symbols. Tickers shows you the current best bid and ask,
as well as the last trade price.

__Attributes__

- `@param symbols Array<string>`: array of symbols i.e [tBTCUSD, tETHUSD]
@return Array [ SYMBOL, BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE,  DAILY_CHANGE_PERC,
  LAST_PRICE, VOLUME, HIGH, LOW ]


## get_derivative_status
```python
BfxRest.get_derivative_status(symbol)
```

Gets platform information for derivative symbol.

__Attributes__

- `@param derivativeSymbol string`: i.e tBTCF0:USTF0
@return [KEY/SYMBOL, MTS, PLACEHOLDER, DERIV_PRICE, SPOT_PRICE, PLACEHOLDER, INSURANCE_FUND_BALANCE4,
    PLACEHOLDER, PLACEHOLDER, FUNDING_ACCRUED, FUNDING_STEP, PLACEHOLDER]


## get_derivative_statuses
```python
BfxRest.get_derivative_statuses(symbols)
```

Gets platform information for a collection of derivative symbols.

__Attributes__

- `@param derivativeSymbols Array<string>`: array of symbols i.e [tBTCF0:USTF0 ...] or ["ALL"]
@return [KEY/SYMBOL, MTS, PLACEHOLDER, DERIV_PRICE, SPOT_PRICE, PLACEHOLDER, INSURANCE_FUND_BALANCE4,
    PLACEHOLDER, PLACEHOLDER, FUNDING_ACCRUED, FUNDING_STEP, PLACEHOLDER]


## get_wallets
```python
BfxRest.get_wallets()
```

Get all wallets on account associated with API_KEY - Requires authentication.

@return Array <models.Wallet>


## get_active_orders
```python
BfxRest.get_active_orders(symbol)
```

Get all of the active orders associated with API_KEY - Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
@return Array <models.Order>


## get_order_history
```python
BfxRest.get_order_history(symbol, start, end, limit=25, sort=-1)
```

Get all of the orders between the start and end period associated with API_KEY
- Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
@return Array <models.Order>


## get_active_position
```python
BfxRest.get_active_position()
```

Get all of the active position associated with API_KEY - Requires authentication.

@return Array <models.Position>


## get_order_trades
```python
BfxRest.get_order_trades(symbol, order_id)
```

Get all of the trades that have been generated by the given order associated with API_KEY
- Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
- `@param order_id string`: id of the order
@return Array <models.Trade>


## get_trades
```python
BfxRest.get_trades(symbol, start, end, limit=25)
```

Get all of the trades between the start and end period associated with API_KEY
- Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
@return Array <models.Trade>


## get_funding_offers
```python
BfxRest.get_funding_offers(symbol)
```

Get all of the funding offers associated with API_KEY - Requires authentication.

@return Array <models.FundingOffer>


## get_funding_offer_history
```python
BfxRest.get_funding_offer_history(symbol, start, end, limit=25)
```

Get all of the funding offers between the start and end period associated with API_KEY
- Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
@return Array <models.FundingOffer>


## get_funding_loans
```python
BfxRest.get_funding_loans(symbol)
```

Get all of the funding loans associated with API_KEY - Requires authentication.

@return Array <models.FundingLoan>


## get_funding_loan_history
```python
BfxRest.get_funding_loan_history(symbol, start, end, limit=25)
```

Get all of the funding loans between the start and end period associated with API_KEY
- Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
@return Array <models.FundingLoan>


## get_funding_credit_history
```python
BfxRest.get_funding_credit_history(symbol, start, end, limit=25)
```

Get all of the funding credits between the start and end period associated with API_KEY
- Requires authentication.

__Attributes__

- `@param symbol string`: pair symbol i.e tBTCUSD
- `@param start int`: millisecond start time
- `@param end int`: millisecond end time
- `@param limit int`: max number of items in response
@return Array <models.FundingCredit>


## submit_funding_offer
```python
BfxRest.submit_funding_offer(symbol,
                             amount,
                             rate,
                             period,
                             funding_type='LIMIT',
                             hidden=False)
```

Submits a new funding offer

__Attributes__

- `@param symbol string`: pair symbol i.e fUSD
- `@param amount float`: funding size
- `@param rate float`: percentage rate to charge per a day
- `@param period int`: number of days for funding to remain active once accepted


## submit_cancel_funding_offer
```python
BfxRest.submit_cancel_funding_offer(fundingId)
```

Cancel a funding offer

__Attributes__

- `@param fundingId int`: the id of the funding offer


## submit_wallet_transfer
```python
BfxRest.submit_wallet_transfer(from_wallet, to_wallet, from_currency,
                               to_currency, amount)
```

Transfer funds between wallets

__Attributes__

- `@param from_wallet string`: wallet name to transfer from i.e margin, exchange
- `@param to_wallet string`: wallet name to transfer to i.e margin, exchange
- `@param from_currency string`: currency symbol to tranfer from i.e BTC, USD
- `@param to_currency string`: currency symbol to transfer to i.e BTC, USD
- `@param amount float`: amount of funds to transfer


## get_wallet_deposit_address
```python
BfxRest.get_wallet_deposit_address(wallet, method, renew=0)
```

Get the deposit address for the given wallet and protocol

__Attributes__

- `@param wallet string`: wallet name i.e margin, exchange
- `@param method string`: transfer protocol i.e bitcoin


## create_wallet_deposit_address
```python
BfxRest.create_wallet_deposit_address(wallet, method)
```

Creates a new deposit address for the given wallet and protocol.
Previously generated addresses remain linked.

__Attributes__

- `@param wallet string`: wallet name i.e margin, exchange
- `@param method string`: transfer protocol i.e bitcoin


## submit_wallet_withdraw
```python
BfxRest.submit_wallet_withdraw(wallet, method, amount, address)
```

Submits a request to withdraw crypto funds to an external wallet.

__Attributes__

- `@param wallet string`: wallet name i.e margin, exchange
- `@param method string`: transfer protocol i.e bitcoin
- `@param amount float`: amount of funds to withdraw
- `@param address string`: external address to withdraw to


## submit_order
```python
BfxRest.submit_order(symbol,
                     price,
                     amount,
                     market_type='LIMIT',
                     hidden=False,
                     price_trailing=None,
                     price_aux_limit=None,
                     oco_stop_price=None,
                     close=False,
                     reduce_only=False,
                     post_only=False,
                     oco=False,
                     aff_code=None,
                     time_in_force=None,
                     leverage=None,
                     gid=None)
```

Submit a new order

__Attributes__

- `@param gid`: assign the order to a group identifier
- `@param symbol`: the name of the symbol i.e 'tBTCUSD
- `@param price`: the price you want to buy/sell at (must be positive)
- `@param amount`: order size: how much you want to buy/sell,
  a negative amount indicates a sell order and positive a buy order
- `@param market_type	Order.Type`: please see Order.Type enum
  amount	decimal string	Positive for buy, Negative for sell
- `@param hidden`: if True, order should be hidden from orderbooks
- `@param price_trailing`:	decimal trailing price
- `@param price_aux_limit`:	decimal	auxiliary Limit price (only for STOP LIMIT)
- `@param oco_stop_price`: set the oco stop price (requires oco = True)
- `@param close`: if True, close position if position present
- `@param reduce_only`: if True, ensures that the executed order does not flip the opened position
- `@param post_only`: if True, ensures the limit order will be added to the order book and not
  match with a pre-existing order
- `@param oco`: cancels other order option allows you to place a pair of orders stipulating
  that if one order is executed fully or partially, then the other is automatically canceled
- `@param aff_code`: bitfinex affiliate code
- `@param time_in_force`:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
- `@param leverage`: the amount of leverage to apply to the order as an integer


## submit_cancel_order
```python
BfxRest.submit_cancel_order(orderId)
```

Cancel an existing open order

__Attributes__

- `@param orderId`: the id of the order that you want to update


## submit_update_order
```python
BfxRest.submit_update_order(orderId,
                            price=None,
                            amount=None,
                            delta=None,
                            price_aux_limit=None,
                            price_trailing=None,
                            hidden=False,
                            close=False,
                            reduce_only=False,
                            post_only=False,
                            time_in_force=None,
                            leverage=None)
```

Update an existing order

__Attributes__

- `@param orderId`: the id of the order that you want to update
- `@param price`: the price you want to buy/sell at (must be positive)
- `@param amount`: order size: how much you want to buy/sell,
  a negative amount indicates a sell order and positive a buy order
- `@param delta`:	change of amount
- `@param price_trailing`:	decimal trailing price
- `@param price_aux_limit`:	decimal	auxiliary Limit price (only for STOP LIMIT)
- `@param hidden`: if True, order should be hidden from orderbooks
- `@param close`: if True, close position if position present
- `@param reduce_only`: if True, ensures that the executed order does not flip the opened position
- `@param post_only`: if True, ensures the limit order will be added to the order book and not
  match with a pre-existing order
- `@param time_in_force`:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
- `@param leverage`: the amount of leverage to apply to the order as an integer


## set_derivative_collateral
```python
BfxRest.set_derivative_collateral(symbol, collateral)
```

Update the amount of callateral used to back a derivative position.

__Attributes__

- `@param symbol of the derivative i.e 'tBTCF0`:USTF0'
- `@param collateral`: amount of collateral/value to apply to the open position

