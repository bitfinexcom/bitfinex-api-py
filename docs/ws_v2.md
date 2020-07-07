
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


# BfxWebsocket
```python
BfxWebsocket(self,
             API_KEY=None,
             API_SECRET=None,
             host='wss://api-pub.bitfinex.com/ws/2',
             manageOrderBooks=False,
             dead_man_switch=False,
             ws_capacity=25,
             logLevel='INFO',
             parse_float=float,
             channel_filter=[],
             *args,
             **kwargs)
```

More complex websocket that heavily relies on the btfxwss module.
This websocket requires authentication and is capable of handling orders.
https://github.com/Crypto-toolbox/btfxwss

### Emitter events:
  - `all` (array|Object): listen for all messages coming through
  - `connected:` () called when a connection is made
  - `disconnected`: () called when a connection is ended (A reconnect attempt may follow)
  - `stopped`: () called when max amount of connection retries is met and the socket is closed
  - `authenticated` (): called when the websocket passes authentication
  - `notification` (Notification): incoming account notification
  - `error` (array): error from the websocket
  - `order_closed` (Order, Trade): when an order has been closed
  - `order_new` (Order, Trade): when an order has been created but not closed. Note: will not be called if order is executed and filled instantly
  - `order_confirmed` (Order, Trade): When an order has been submitted and received
  - `wallet_snapshot` (array[Wallet]): Initial wallet balances (Fired once)
  - `order_snapshot` (array[Order]): Initial open orders (Fired once)
  - `positions_snapshot` (array): Initial open positions (Fired once)
  - `positions_new` (array): Initial open positions (Fired once)
  - `positions_update` (array): An active position has been updated
  - `positions_close` (array): An active position has closed
  - `wallet_update` (Wallet): Changes to the balance of wallets
  - `status_update` (Object): New platform status info
  - `seed_candle` (Object): Initial past candle to prime strategy
  - `seed_trade` (Object): Initial past trade to prime strategy
  - `funding_offer_snapshot` (array): Opening funding offer balances
  - `funding_loan_snapshot` (array): Opening funding loan balances
  - `funding_credit_snapshot` (array): Opening funding credit balances
  - `balance_update` (array): When the state of a balance is changed
  - `new_trade` (array): A new trade on the market has been executed
  - `new_ticker` (Ticker|FundingTicker): A new ticker update has been published
  - `new_funding_ticker` (FundingTicker): A new funding ticker update has been published
  - `new_trading_ticker` (Ticker): A new trading ticker update has been published
  - `trade_update` (array): A trade on the market has been updated
  - `new_candle` (array): A new candle has been produced
  - `margin_info_updates` (array): New margin information has been broadcasted
  - `funding_info_updates` (array): New funding information has been broadcasted
  - `order_book_snapshot` (array): Initial snapshot of the order book on connection
  - `order_book_update` (array): A new order has been placed into the ordebrook
  - `subscribed` (Subscription): A new channel has been subscribed to
  - `unsubscribed` (Subscription): A channel has been un-subscribed


## enable_flag
```python
BfxWebsocket.enable_flag(flag)
```

Enable flag on websocket connection

__Attributes__

- `flag (int)`: int flag value


## subscribe_order_book
```python
BfxWebsocket.subscribe_order_book(symbol)
```

Subscribe to an orderbook data feed

__Attributes__

- `@param symbol`: the trading symbol i.e 'tBTCUSD'


## subscribe_candles
```python
BfxWebsocket.subscribe_candles(symbol, timeframe)
```

Subscribe to a candle data feed

__Attributes__

- `@param symbol`: the trading symbol i.e 'tBTCUSD'
- `@param timeframe`: resolution of the candle i.e 15m, 1h


## subscribe_trades
```python
BfxWebsocket.subscribe_trades(symbol)
```

Subscribe to a trades data feed

__Attributes__

- `@param symbol`: the trading symbol i.e 'tBTCUSD'


## subscribe_ticker
```python
BfxWebsocket.subscribe_ticker(symbol)
```

Subscribe to a ticker data feed

__Attributes__

- `@param symbol`: the trading symbol i.e 'tBTCUSD'


## subscribe_derivative_status
```python
BfxWebsocket.subscribe_derivative_status(symbol)
```

Subscribe to a status data feed

__Attributes__

- `@param symbol`: the trading symbol i.e 'tBTCUSD'


## subscribe
```python
BfxWebsocket.subscribe(*args, **kwargs)
```

Subscribe to a new channel

__Attributes__

- `@param channel_name`: the name of the channel i.e 'books', 'candles'
- `@param symbol`: the trading symbol i.e 'tBTCUSD'
- `@param timeframe`: sepecifies the data timeframe between each candle (only required
  for the candles channel)


## unsubscribe
```python
BfxWebsocket.unsubscribe(*args, **kwargs)
```

Unsubscribe from the channel with the given chanId

__Attributes__

- `@param onComplete`: function called when the bitfinex websocket resoponds with
  a signal that confirms the subscription has been unsubscribed to


## resubscribe
```python
BfxWebsocket.resubscribe(*args, **kwargs)
```

Unsubscribes and then subscribes to the channel with the given Id

This function is mostly used to force the channel to produce a fresh snapshot.


## unsubscribe_all
```python
BfxWebsocket.unsubscribe_all(*args, **kwargs)
```

Unsubscribe from all channels.


## resubscribe_all
```python
BfxWebsocket.resubscribe_all(*args, **kwargs)
```

Unsubscribe and then subscribe to all channels


## submit_order
```python
BfxWebsocket.submit_order(*args, **kwargs)
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

@param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
@param leverage: the amount of leverage to apply to the order as an integer
@param onConfirm: function called when the bitfinex websocket receives signal that the order
  was confirmed
@param onClose: function called when the bitfinex websocket receives signal that the order
  was closed due to being filled or cancelled


## update_order
```python
BfxWebsocket.update_order(*args, **kwargs)
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
- `@param time_in_force`: datetime for automatic order cancellation ie. 2020-01-01 10:45:23
- `@param leverage`: the amount of leverage to apply to the order as an integer
- `@param onConfirm`: function called when the bitfinex websocket receives signal that the order
  was confirmed
- `@param onClose`: function called when the bitfinex websocket receives signal that the order
  was closed due to being filled or cancelled


## cancel_order
```python
BfxWebsocket.cancel_order(*args, **kwargs)
```

Cancel an existing open order

__Attributes__

- `@param orderId`: the id of the order that you want to update
- `@param onConfirm`: function called when the bitfinex websocket receives signal that the
                  order
  was confirmed
- `@param onClose`: function called when the bitfinex websocket receives signal that the order
  was closed due to being filled or cancelled


## cancel_order_group
```python
BfxWebsocket.cancel_order_group(*args, **kwargs)
```

Cancel a set of orders using a single group id.


## cancel_all_orders
```python
BfxWebsocket.cancel_all_orders(*args, **kwargs)
```

Cancel all existing open orders

This function closes all open orders.


## cancel_order_multi
```python
BfxWebsocket.cancel_order_multi(*args, **kwargs)
```

Cancel existing open orders as a batch

__Attributes__

- `@param ids`: an array of order ids
- `@param gids`: an array of group ids

