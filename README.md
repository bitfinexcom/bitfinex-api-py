# Official Python `bfxapi`
This repo contains an official python library that is used to connect to the both the Bitfinex api and the Honey Frameworks data-server. The library communicates with these servers using both websockets connection and a its REST interface.

Install dependencies
```
pip3 install -r requirements.txt
```
Run the trades/candles example:
```
cd bfxapi/examples
python3 subsribe_trades_candles.py
```

## `bfxapi.LiveWebsocket`
The websocket exposes a collection of events that are triggered when certain data is received. When subscribing to an event you are able to pass either a standard function or an asyncio co-routine Here is a full list of available events:

- `all` (array|json): listen for all messages coming through
- `connected:` () called when a connection is made
- `authenticated` (): called when the websocket passes authentication
- `notification` (array): incoming account notification
- `error` (array): error from the websocket
- `order_closed` (Order, Trade): when an order has been closed
- `order_new` (Order, Trade): when an order has been created but not closed. Note: will not be called if order is executed and filled instantly
- `order_confirmed` (Order, Trade): When an order has been submitted and received
- `wallet_snapshot` (array): Initial wallet balances (Fired once)
- `order_snapshot` (array): Initial open orders (Fired once)
- `positions_snapshot` (array): Initial open positions (Fired once)
- `wallet_update` (array): changes to the balance of wallets
- `seed_candle` (json): initial past candle to prime strategy
- `seed_trade` (json): initial past trade to prime strategy
- `funding_offer_snapshot` (array): opening funding offer balances
- `funding_loan_snapshot` (array): opening funding loan balances
- `funding_credit_snapshot` (array): opening funding credit balances
- `balance_update` (array): when the state of a balance is changed
- `new_trade` (array): a new trade on the market has been executed
- `new_candle` (array): a new candle has been produced
- `margin_info_updates` (array): new margin information has been broadcasted
- `funding_info_updates` (array): new funding information has been broadcasted
- `order_book_snapshot` (array): initial snapshot of the order book on connection
- `order_book_update` (array): a new order has been placed into the ordebrook

For example. If you wanted to subscribe to all of the trades on the `tBTCUSD` market, then you can simply listen to the `new_trade` event. For Example:

```
ws = LiveBfxWebsocket(
  logLevel='INFO'
)

@ws.on('new_trade')
def log_trade(trade):
  print ("New trade: {}".format(trade))

@ws.on('connected')
def start():
  ws.subscribe('trades', 'tBTCUSD')

ws.run()
```

NOTE: Instead of using the python decorators, you can also listen to events via function call:

```
ws.on('new_trade', log_trade)
```

### Exposed Async Functions

- `subscribe(channel_name, symbol, timeframe=None, **kwargs)`
  Subscribes the socket to a data feed such as 'trades' or 'candles'.
- `submit_order(symbol, price, amount, market_type, hidden=False, onComplete=None, onError=None, *args, **kwargs)`
  Submits an order to the Bitfinex api. If the order is successful then the order_closed event will be triggered and the onComplete function will also be called if provided in the parameters.
- `update_order(orderId, price=None, amount=None, delta=None, price_aux_limit=None, price_trailing=None, flags=None, time_in_force=None, onComplete=None, onError=None)`
  Updates the given order_id with the provided values
- `cancel_order(self, orderId, onComplete=None, onError=None):`
  Cancels the order with the given order id
- `cancel_order_multi(self, orderIds, onComplete=None, onError=None)`
  Cancels multiple orders in a batch.

### Exposed Functions

- `on(event, function)`
  Subscribes the function to be triggered on the given event.
- `once(event, function)`
  Subscribes the function to the given event but only triggers once.
