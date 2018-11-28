
```
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


# Official Python `bfxapi`
This is an official python library that is used to connect interact with the Bitfinex api. Currently it only has support for websockets but will soon have Rest functionality as well.

Install dependencies
```
pip3 install -r requirements.txt
```
Run the trades/candles example:
```
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

```
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

```
await bfx.ws.submit_order('tBTCUSD', 19000, 0.01, 'EXCHANGE LIMIT')
```

### Listen for completion
```
@bfx.ws.on('order_confirmed')
async def order_completed(order, trade):
  print ("Order has been confrmed")
```

### Get wallets
```
wallets = bfxapi.wallets.get_wallets()
# [ Wallet <'exchange_BTC' balance='41.25809589' unsettled='0'>,
#   Wallet <'exchange_USD' balance='62761.86070104' unsettled='0'> ]
```

### Close all orders
```
await bfx.ws.close_all_orders()
```


## `bfxapi.ws` events
The websocket exposes a collection of events that are triggered when certain data is received. When subscribing to an event you are able to pass either a standard function or an asyncio co-routine Here is a full list of available events:

- `all` (array|json): listen for all messages coming through
- `connected:` () called when a connection is made
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
- `subscribed` (Subscription): a new channel has been subscribed to
- `unsubscribed` (Subscription): a channel has been un-subscribed




# `bfxapi.ws` interface

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

#### `submit_order(symbol, price, amount, market_type, hidden=False, onComplete=None, onError=None, *args, **kwargs)`
  
  Submits an order to the Bitfinex api. If the order is successful then the order_closed event will be triggered and the onComplete function will also be called if provided in the parameters.

#### `update_order(orderId, price=None, amount=None, delta=None, price_aux_limit=None, price_trailing=None, flags=None, time_in_force=None, onComplete=None, onError=None)`
  
  Attempts to update an order with the given values. If the order is no longer open then the update will be ignored.

#### `close_order(self, orderId, onComplete=None, onError=None):`
  
  Close the order with the given orderId if it still open.

#### `close_all_orders()`
  
  Tells the OrderManager to close all of the open orders

#### `close_orders_multi(self, orderIds)`
  
  Takes an array of orderIds and closes them all.

# `bfxapi.wallets`

### `get_wallets()`

  Returns an array of wallets that represent the users balance in the different currencies

# `Order obj`

### `close()`

  Signals Bitfinex to close the order

### `update(self, price=None, amount=None, delta=None, price_aux_limit=None,        price_trailing=None, flags=None, time_in_force=None)`

  Signals Bitfinex to update the order with the given values

### `isOpen()`

  Returns true if the order has not been closed

### `isPending()`

  Returns true if Bitfinex has not responded to confirm the order has been received

### `isConfirmed()`

  Returns true if Bitfinex has responded to confirm the order

# `Subscription obj`

### `subscribe()`

  Sends a subscribe command to start receiving data

### `unsubscribe()`

  Sends a unsubscribe command to stop receiving data

### `is_subscribed()`

  Returns true if the subscription is open and receiving data


# Examples

For more info on how to use this library please see the example scripts in the `bfxapi/examples` directory.
