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
- `order_closed` (Order, Trade): when an order confirmation is received
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

### Exposed Functions

- `subscribe(channel_name, symbol, timeframe=None, **kwargs)`
  Subscribes the socket to a data feed such as 'trades' or 'candles'.
- `submit_order(symbol, price, amount, market_type, hidden=False, onComplete=None, onError=None, *args, **kwargs)`
  Submits an order to the Bitfinex api. If the order is successful then the order_closed event will be triggered and the onComplete function will also be called if provided in the parameters.
- `on(event, function)`
  subscribes the function to be triggered on the given event.


## `bfxapi.DataServerWebsocket`

The data-server websocket is used for retrieving large amounts of historical data from a `bfx-hf-data-server` instance. The library then takes all of the incoming historical data from the server and pushes it down the `new_trade` and `new_candle` events. For information on how to start a data-server instance please visit the repo at: https://github.com/bitfinexcom/bfx-hf-data-server

A list of events available:

- `connected`: connection is made
- `new_trade`: a historical trade item is received
- `new_candle`: a historical candle item is received
- `done`: backtest has finished running

An example of a script that loads all of the historical trades for symbol `tBTCUSD` over the last 2 days:

```
ws = DataServerWebsocket(
  symbol='tBTCUSD',
  host='ws://localhost:8899'
)

@ws.on('new_trade')
def trade(trade):
  print ("Backtest trade: {}".format(trade))

@ws.on('done')
def finish():
  print ("Backtest complete!")

now = int(round(time.time() * 1000))
then = now - (1000 * 60 * 60 * 24 * 2) # 2 days ago
ws.run(then, now)

```

<br>
<br>
Please see the <b>bfxapi/examples</b> folder. There you will be able to find working scripts that submit orders, establish a connect and run backtests.
