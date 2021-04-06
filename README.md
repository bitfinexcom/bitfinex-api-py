# Bitfinex Trading Library for Python - Bitcoin, Ethereum, Ripple and more

![https://api.travis-ci.org/bitfinexcom/bitfinex-api-py.svg?branch=master](https://api.travis-ci.org/bitfinexcom/bitfinex-api-py.svg?branch=master)

A Python reference implementation of the Bitfinex API for both REST and websocket interaction.

# Features
- Official implementation
- Websocket V2 and Rest V2
- Connection multiplexing
- Order and wallet management
- All market data feeds

## Installation

Clone package into PYTHONPATH:
```sh
git clone https://github.com/bitfinexcom/bitfinex-api-py.git
cd bitfinex-api-py
```

Or via pip:
```sh
python3 -m pip install bitfinex-api-py
```

Run the trades/candles example:
```sh
cd bfxapi/examples/ws
python3 subscribe_trades_candles.py
```

## Quickstart

```python
import os
import sys
from bfxapi import Client, Order

bfx = Client(
  API_KEY='<YOUR_API_KEY>',
  API_SECRET='<YOUR_API_SECRET>'
)

@bfx.ws.on('authenticated')
async def submit_order(auth_message):
  await bfx.ws.submit_order('tBTCUSD', 19000, 0.01, Order.Type.EXCHANGE_MARKET)

bfx.ws.run()
```

## Docs

* <b>[V2 Rest](docs/rest_v2.md)</b> - Documentation
* <b>[V2 Websocket](docs/ws_v2.md)</b> - Documentation

## Examples

#### Authenticate

```python
bfx = Client(
  API_KEY='<YOUR_API_KEY>',
  API_SECRET='<YOUR_API_SECRET>'
)

@bfx.ws.on('authenticated')
async def do_something():
  print ("Success!")

bfx.ws.run()
```

#### Subscribe to trades

```python
from bfxapi import Client

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET
)

@bfx.ws.on('new_trade')
def log_trade(trade):
  print ("New trade: {}".format(trade))

@bfx.ws.on('connected')
def start():
  bfx.ws.subscribe('trades', 'tBTCUSD')

bfx.ws.run()
```

#### Withdraw from wallet via REST

```python
bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)
response = await bfx.rest.submit_wallet_withdraw("exchange", "tetheruse", 5, "0xc5bbb852f82c24327693937d4012f496cff7eddf")
print ("Address: ", response.notify_info)
```
See the <b>[examples](https://github.com/bitfinexcom/bitfinex-api-py/tree/master/examples)</b> directory for more, like:

- [Creating/updating an order](https://github.com/bitfinexcom/bitfinex-api-py/blob/master/bfxapi/examples/ws/send_order.py)
- [Subscribing to orderbook updates](https://github.com/bitfinexcom/bitfinex-api-py/blob/master/bfxapi/examples/ws/resubscribe_orderbook.py)
- [Withdrawing crypto](https://github.com/bitfinexcom/bitfinex-api-py/blob/master/bfxapi/examples/rest/transfer_wallet.py)
- [Submitting a funding offer](https://github.com/bitfinexcom/bitfinex-api-py/blob/master/bfxapi/examples/rest/create_funding.py)

For more info on how to use this library please see the example scripts in the `bfxapi/examples` directory. Here you will find usage of all interface exposed functions for both the rest and websocket.

Also please see [this medium article](https://medium.com/@Bitfinex/15f201ad20d4) for a tutorial.

## FAQ

### Is there any rate limiting?

For a Websocket connection there is no limit to the number of requests sent down the connection (unlimited order operations) however an account can only create 15 new connections every 5 mins and each connection is only able to subscribe to 30 inbound data channels. Fortunately this library handles all of the load balancing/multiplexing for channels and will automatically create/destroy new connections when needed, however the user may still encounter the max connections rate limiting error.

For rest the base limit per-user is 1,000 orders per 5 minute interval, and is shared between all account API connections. It increases proportionally to your trade volume based on the following formula:

1000 + (TOTAL_PAIRS_PLATFORM * 60 * 5) / (250000000 / USER_VOL_LAST_30d)

Where TOTAL_PAIRS_PLATFORM is the number of pairs on the Bitfinex platform (currently ~101) and USER_VOL_LAST_30d is in USD.

### Will I always receive an `on` packet?

No; if your order fills immediately, the first packet referencing the order will be an `oc` signaling the order has closed. If the order fills partially immediately after creation, an `on` packet will arrive with a status of `PARTIALLY FILLED...`

For example, if you submit a `LIMIT` buy for 0.2 BTC and it is added to the order book, an `on` packet will arrive via ws2. After a partial fill of 0.1 BTC, an `ou` packet will arrive, followed by a final `oc` after the remaining 0.1 BTC fills.

On the other hand, if the order fills immediately for 0.2 BTC, you will only receive an `oc` packet.

### My websocket won't connect!

Did you call `client.Connect()`? :)

### nonce too small

I make multiple parallel request and I receive an error that the nonce is too small. What does it mean?

Nonces are used to guard against replay attacks. When multiple HTTP requests arrive at the API with the wrong nonce, e.g. because of an async timing issue, the API will reject the request.

If you need to go parallel, you have to use multiple API keys right now.

### How do `te` and `tu` messages differ?

A `te` packet is sent first to the client immediately after a trade has been matched & executed, followed by a `tu` message once it has completed processing. During times of high load, the `tu` message may be noticably delayed, and as such only the `te` message should be used for a realtime feed.

### What are the sequence numbers for?

If you enable sequencing on v2 of the WS API, each incoming packet will have a public sequence number at the end, along with an auth sequence number in the case of channel `0` packets. The public seq numbers increment on each packet, and the auth seq numbers increment on each authenticated action (new orders, etc). These values allow you to verify that no packets have been missed/dropped, since they always increase monotonically.

### What is the difference between R* and P* order books?

Order books with precision `R0` are considered 'raw' and contain entries for each order submitted to the book, whereas `P*` books contain entries for each price level (which aggregate orders).


## Contributing

1. Fork it ( https://github.com/[my-github-username]/bitfinex/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request

### Publish to Pypi

```
python setup.py sdist
twine upload dist/*
```
