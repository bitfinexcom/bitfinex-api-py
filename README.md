
```python
from bfxapi import Client

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

@bfx.ws.on('new_trade')
def log_trade(trade):
  print ("New trade: {}".format(trade))

@bfx.ws.on('connected')
def start():
  bfx.ws.subscribe('trades', 'tBTCUSD')

bfx.ws.run()
```


# Bitfinex Trading API for Python. Bitcoin, Ether and Litecoin trading
This is an official python library that is used to connect interact with the Bitfinex api. Currently it only has support for websockets but will soon have Rest functionality as well.

Install dependencies
```sh
pip3 install -r requirements.txt
```
Run the trades/candles example:
```sh
cd bfxapi/examples
python3 subsribe_trades_candles.py
```

# Features
- Fast websocket connection
- Event based routing
- Subscribe to trade, candles and orderbook channels
- Authenticate with api key/secret
- Orderbook checksum validation
- Create, update and close orders
- Track wallet updates

# Quickstart

### Authenticate

```python
bfx = Client(
  API_KEY='<YOUR_API_KEY>'
  API_SECRET='<YOUR_API_SECRET>'
)

@bfx.ws.on('authenticated')
async def do_something():
  print ("Success!")

bfx.ws.run()
```

### Submit limit order

```python
from bfxapi import Order
await bfx.ws.submit_order('tBTCUSD', 100, 0.01, Order.Type.EXCHANGE_MARKET)
```

### Listen for completion
```python
@bfx.ws.on('order_confirmed')
async def order_completed(order, trade):
  print ("Order has been confrmed")
```

### Get wallets
```python
wallets = bfxapi.ws.wallets.get_wallets()
# [ Wallet <'exchange_BTC' balance='41.25809589' unsettled='0'>,
#   Wallet <'exchange_USD' balance='62761.86070104' unsettled='0'> ]
```

### Order manipulation
All order function support onConfirm and onClose async callbacks. onConfirm is fired when we receive a signal from the websocket that the order has been confirmed. onClose is fired when we receive a signal that the order has either been filled or canceled.

```python

async def on_confirm(order):
  await bfx.ws.update_order(order.id, price=1000)

await bfx.ws.submit_order('tBTCUSD', 800, 0.1, onConfirm=on_confirm)
```

### Close all orders
```python
await bfx.ws.close_all_orders()
```


## `bfxapi.ws` events
The websocket exposes a collection of events that are triggered when certain data is received. When subscribing to an event you are able to pass either a standard function or an asyncio co-routine Here is a full list of available events:

- `all` (array|json): listen for all messages coming through
- `connected:` () called when a connection is made
- `disconnected`: () called when a connection is ended (A reconnect attempt may follow)
- `stopped`: () called when max amount of connection retries is met and the socket is closed
- `authenticated` (): called when the websocket passes authentication
- `notification` (array): incoming account notification
- `error` (array): error from the websocket
- `order_closed` (Order, Trade): when an order has been closed
- `order_new` (Order, Trade): when an order has been created but not closed. Note: will not be called if order is executed and filled instantly
- `order_confirmed` (Order, Trade): When an order has been submitted and received
- `wallet_snapshot` (array[Wallet]): Initial wallet balances (Fired once)
- `order_snapshot` (array[Order]): Initial open orders (Fired once)
- `positions_snapshot` (array): Initial open positions (Fired once)
- `wallet_update` (Wallet): changes to the balance of wallets
- `status_update` (json): new platform status info
- `seed_candle` (json): initial past candle to prime strategy
- `seed_trade` (json): initial past trade to prime strategy
- `funding_offer_snapshot` (array): opening funding offer balances
- `funding_loan_snapshot` (array): opening funding loan balances
- `funding_credit_snapshot` (array): opening funding credit balances
- `balance_update` (array): when the state of a balance is changed
- `new_trade` (array): a new trade on the market has been executed
- `trade_update` (array): a trade on the market has been updated
- `new_candle` (array): a new candle has been produced
- `margin_info_updates` (array): new margin information has been broadcasted
- `funding_info_updates` (array): new funding information has been broadcasted
- `order_book_snapshot` (array): initial snapshot of the order book on connection
- `order_book_update` (array): a new order has been placed into the ordebrook
- `subscribed` (Subscription): a new channel has been subscribed to
- `unsubscribed` (Subscription): a channel has been un-subscribed




# bfxapi ws interface

#### `on(event, function)`

  Subscribe a given function to be called when an event fires

#### `once(event, function)`

  Subscribes the function to the given event but only triggers once.

#### `subscribe(channel_name, symbol, timeframe=None, **kwargs)`
    
  Subscribes the socket to a data feed such as 'trades' or 'candles'.

#### `unsubscribe(chanId, onComplete=None)`
    
  Unsubscribes from the given data feed

#### `resubscribe(chanId, onComplete=None)`
  
  Unsubscribes and then subscribes to the given data feed. Usually used to trigger a snapshot response from the API.

#### `unsubscribe_all()`
    
  Unsubscribe from all data feeds.

#### `resubscribe_all(chanId, onComplete=None)`
    
  Unsubscribe and subscribe to all data feeds

#### `submit_order(symbol, price, amount, market_type, hidden=False, onConfirm=None,   onClose=None, *args, **kwargs)`
  
  Submits an order to the Bitfinex api. When it has been verified that bitfine xhas received the order then the `onConfirm` callback will be called followed by the `order_confirmed` event. Once it has been verified that the order has completely closed due to either being filled or canceled then the `onClose` function will be called, followed by the `order_closed` event.

#### `update_order(orderId, price=None, amount=None, delta=None, price_aux_limit=None, price_trailing=None, flags=None, time_in_force=None, onConfirm=None, onClose=None)`
  
  Attempts to update an order with the given values. If the order is no longer open then the update will be ignored.

#### `close_order(self, orderId, onConfirm=None, onClose=None):`
  
  Close the order with the given orderId if it still open.

#### `close_all_orders()`
  
  Tells the OrderManager to close all of the open orders

#### `close_orders_multi(self, orderIds)`
  
  Takes an array of orderIds and closes them all.

## bfxapi.ws.wallets

### `get_wallets()`

  Returns an array of wallets that represent the users balance in the different currencies

## `bfx.ws.Subscription obj`

### `subscribe()`

  Sends a subscribe command to start receiving data

### `unsubscribe()`

  Sends a unsubscribe command to stop receiving data

### `is_subscribed()`

  Returns true if the subscription is open and receiving data

# bfxapi rest interface

### `get_public_candles(symbol, start, end, section='hist', tf='1m', limit="100", sort=-1 `

  Get All of the public candles between the given start and end period

### `get_public_trades(symbol, start, end, limit="100", sort=-1)`

Get all of the public trades between the start and end period

### `get_public_books(symbol, precision="P0", length=25)`

Get the public orderbook of a given symbol

### `get_public_ticker(symbol)`

  Get tickers for the given symbol. Tickers shows you the current best bid and ask,
  as well as the last trade price.

### `get_public_tickers(symbols)`

  Get tickers for the given symbols. Tickers shows you the current best bid and ask,
  as well as the last trade price.

### `get_derivative_status(symbol)`

  Get derivative platform information for the given symbol.

### `get_derivative_statuses(symbols)`

  Get derivative platform information for the given collection of symbols.

### `get_wallets()`

  Get all wallets on account associated with API_KEY - Requires authentication.

### `get_active_orders(symbol)`

  Get all of the active orders associated with API_KEY - Requires authentication.

### `get_order_history(symbol, start, end, limit=25, sort=-1)`

  Get all of the orders between the start and end period associated with API_KEY
  - Requires authentication.

### `get_active_positions()`

  Get all of the active position associated with API_KEY - Requires authentication.

### `get_order_trades(symbol, order_id)`

  Get all of the trades that have been generated by the given order associated with API_KEY - Requires authentication.

### `get_trades(symbol, start, end, limit=25)`

  Get all of the trades between the start and end period associated with API_KEY
  - Requires authentication.

### `get_funding_offers(symbol)

  Get all of the funding offers associated with API_KEY - Requires authentication.

### `get_funding_offer_history(symbol, start, end, limit=25)`

  Get all of the funding offers between the start and end period associated with API_KEY - Requires authentication.

### `get_funding_loans(symbol)`

  Get all of the funding loans associated with API_KEY - Requires authentication.

### `get_funding_loan_history(symbol, start, end, limit=25)`

  Get all of the funding loans between the start and end period associated with API_KEY - Requires authentication.

### `get_funding_credits(symbol)`

  Get all of the funding credits associated with API_KEY - Requires authentication.

### `get_funding_credit_history(symbol, start, end, limit=25)`

  Get all of the funding credits between the start and end period associated with API_KEY - Requires authentication.

### `set_derivative_collateral(symbol, collateral)`

  Set the amount of collateral used to back a derivative position.

# Examples

For more info on how to use this library please see the example scripts in the `bfxapi/examples` directory. Here you will find usage of all interface exposed functions for both the rest and websocket.

Also please see [this medium article](https://medium.com/@Bitfinex/15f201ad20d4) for a tutorial.

## Contributing

1. Fork it ( https://github.com/[my-github-username]/bitfinex/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
