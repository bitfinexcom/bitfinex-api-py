# bitfinex-api-py (v3-beta)

Official implementation of the [Bitfinex APIs (V2)](https://docs.bitfinex.com/docs) for `Python 3.8+`.

> **DISCLAIMER:** \
Production use of v3.0.0b1 (and all future beta versions) is HIGHLY discouraged. \
Beta versions should not be used in applications which require user authentication. \
Provide your API-KEY/API-SECRET, and manage your account and funds at your own risk.

### Features
- User-friendly implementations for 75+ public and authenticated REST endpoints.
    * A complete list of available REST endpoints can be found [here](https://docs.bitfinex.com/reference).
- New WebSocket client to ensure fast, secure and persistent connections.
    * Support for all public channels + authenticated events and inputs (a list can be found [here](https://docs.bitfinex.com/docs/ws-public)).
    * Automatic reconnection system in case of network failure (both client and server side).
        - The WebSocket client logs every reconnection failure, success and attempt (as well as other events).
    * Connection multiplexing to allow subscribing to a large number of public channels (without affecting performances).
        - The WebSocket server sets a limit of 25 subscriptions per connection, connection multiplexing allows the WebSocket client to bypass this limit.
- Full type-hinting and type-checking support with [`mypy`](https://github.com/python/mypy). 
    * This allow text editors to show helpful hints about the value of a variable: ![example](https://i.imgur.com/aDjapcN.png "Type-hinting example on a random code snippet")

---

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Using the WebSocket client](#using-the-websocket-client)
    * [Running the client](#running-the-client)
    * [Subscribing to public channels](#subscribing-to-public-channels)
    * [Listening to events](#listening-to-events)
    * [Authentication with API-KEY and API-SECRET](#authentication-with-api-key-and-api-secret)
4. [Building the source code](#building-the-source-code)
    * [Testing (with unittest)](#testing-with-unittest)
    * [Linting the project with pylint](#linting-the-project-with-pylint)
    * [Using mypy to ensure correct type-hinting](#using-mypy-to-ensure-correct-type-hinting)
5. [How to contribute](#how-to-contribute)
    * [License](#license)

## Installation

To install the latest beta release of `bitfinex-api-py`:
```bash
python3 -m pip install --pre bitfinex-api-py
```
To install a specific beta version:
```bash
python3 -m pip install bitfinex-api-py==3.0.0b1
```

## Basic usage

## Using the WebSocket client

```python
bfx = Client(wss_host=PUB_WSS_HOST)
```

`Client::wss` contains an instance of `BfxWebSocketClient` (core implementation of the WebSocket client). \
The `wss_host` argument is used to indicate the URL to which the WebSocket client should connect. \
The `bfxapi` package exports 2 constants to quickly set this URL:

Constant | URL | When to use
--- | --- | ---
WSS_HOST | wss://api.bitfinex.com/ws/2 | Suitable for all situations, with support for authentication.
PUB_WSS_HOST | wss://api-pub.bitfinex.com/ws/2 | Recommended for connections that do not require authentication.

> **NOTE:** The `wss_host` parameter is optional, and the default value is WSS_HOST.

### Running the client

### Subscribing to public channels

Users can subscribe to public channels using the coroutine `BfxWebSocketClient::subscribe`:
```python
await bfx.wss.subscribe("ticker", symbol="tBTCUSD")
```

#### Setting a custom `sub_id`

The client generates a random and unique `sub_id` for each subscription. \
However, it is possible to force this value by using the `sub_id` argument:

```python
await bfx.wss.subscribe("candles", key="trade:1m:tBTCUSD", sub_id="507f1f77bcf86cd799439011")
```

#### Using the `Channel` enumeration

`Channel` is an enumeration that contains the names of all the available public channels:
```python
from bfxapi.websocket.enums import Channel
```

You can use `Channel` while subscribing to a new public channel:
```python
await bfx.wss.subscribe(Channel.CANDLES, key="trade:1m:tBTCUSD", sub_id="507f1f77bcf86cd799439011")
```

### Listening to events

Whenever the WebSocket client receives data, it will emit a specific event. \
Users can either ignore those events or listen for them by registering callback functions. \
To add a listener for a specific event, users can use the `BfxWebSocketClient::on` decorator:
```python
@bfx.wss.on("candles_update")
def on_candles_update(sub: subscriptions.Candles, candle: Candle):
    print(f"Candle update for key <{sub['key']}>: {candle}")
```

The same can be achieved without using decorators:
```python
bfx.wss.on("candles_update", callback=on_candles_update)
```

You can pass any number of events to register for the same callback function:
```python
bfx.wss.on("t_ticker_update", "f_ticker_update", callback=on_ticker_update)
```

> **NOTE:** Callback functions can be either synchronous or asynchronous, in fact the client fully support coroutines (`asyncio`).

#### The `open` event

When the connection to the server is established, the client will emit the `open` event. \
This is the right place for all bootstrap activities, including subscribing to public channels.

```python
@bfx.wss.once("open")
async def on_open():
    await bfx.wss.subscribe(Channel.TICKER, symbol="tBTCUSD")
```

#### The `authenticated` event


If authentication succeeds, the client will emit the `authenticated` event. \
All operations that require authentication must be performed after the emission of this event. \
The `data` argument contains information regarding the authentication, such as the `userId`, the `auth_id`, etc...

```python
@bfx.wss.once("authenticated")
def on_authenticated(data):
    print(f"Successful login for user <{data['userId']}>.)
```

#### Using `BfxWebSocketClient::once` instead of `BfxWebSocketClient::on`

For events that are expected to be emitted only once, it is highly recommended to use `BfxWebSocketClient::once`. \
This prevents the client from emitting those events again, for example, after the connection is re-established following a network failure:

```python
@bfx.wss.once("t_book_snapshot")
def on_t_book_snapshot(sub: subscriptions.Book, snapshot: List[TradingPairBook]):
    print(f"The snapshot ({sub['symbol']}) contains {len(snapshot)} price points.")
```

### Authentication with API-KEY and API-SECRET

## Building the source code

### Testing (with unittest)

### Linting the project with pylint

### Using mypy to ensure correct type-hinting

## How to contribute

### License
This project is released under the `Apache License 2.0`.

The complete license can be found here: https://www.apache.org/licenses/LICENSE-2.0.
