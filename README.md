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

---

### Index

* [WebSocket Client documentation](#websocket-client-documentation)
* [Building the source code](#building-the-source-code)
* [How to contribute](#how-to-contribute)

---

# WebSocket Client documentation

1. [Instantiating the client](#instantiating-the-client)
    * [Authentication](#authentication)
    * [Configuring the logger](#configuring-the-logger)
2. [Running the client](#running-the-client)
    * [Closing the client](#closing-the-client)
    * [Connection multiplexing](#connection-multiplexing)
3. [Subscribing to public channels](#subscribing-to-public-channels)
    * [Setting a custom `sub_id`](#setting-a-custom-sub_id)
4. [Listening to events](#listening-to-events)
5. [Events](#events)
    * [`open`](#open)
    * [`authenticated`](#authenticated)
6. [Sending custom notifications](#sending-custom-notifications)
7. [Handling reconnections in case of network failure](#handling-reconnections-in-case-of-network-failure)

## Instantiating the client

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

### Authentication

### Configuring the logger

`log_filename` (`Optional[str]`, default: `None`): \
Relative path of the file where to save the logs the client will emit. \
If not given, the client will emit logs on `stdout` (`stderr` for errors and warnings).

`log_level` (`str`, default: `"INFO"`): \
Available log levels are (in order): `ERROR`, `WARNING`, `INFO` and `DEBUG`. \
The client will only log messages whose level is lower than or equal to `log_level`. \
For example, if `log_level=WARNING`, the client will only log errors and warnings.

```python
bfx = Client(
    [...],
    log_filename="2023-03-26.log",
    log_level="WARNING"
)
```


## Running the client

The client can be run using `BfxWebSocketClient::run`:
```python
bfx.wss.run()
```

If an event loop is already running, users can start the client with `BfxWebSocketClient::start`:
```python
await bfx.wss.start()
```

### Closing the client

```python
await bfx.wss.close(code=1001, reason="Going Away")
```

### Connection multiplexing

`BfxWebSocketClient::run` and `BfxWebSocketClient::start` accept a `connections` argument:
```python
bfx.wss.run(connections=3)
```

`connections` indicates the number of connections to run concurrently (through connection multiplexing).

Each of these connections can handle up to 25 subscriptions to public channels. \
So, using `N` connections will allow the client to handle at most `N * 25` subscriptions. \
You should always use the minimum number of connections necessary to handle all the subscriptions that will be made.

For example, if you know that your application will subscribe to 75 public channels, 75 / 25 = 3 connections will be enough to handle all the subscriptions.

The default number of connections is 5; therefore, if the `connections` argument is not given, the client will be able to handle a maximum of 25 * 5 = 125 subscriptions.

Keep in mind that using a large number of connections could slow down the client performance.

The use of more than 20 connections is not recommended.

## Subscribing to public channels

Users can subscribe to public channels using `BfxWebSocketClient::subscribe`:
```python
await bfx.wss.subscribe("ticker", symbol="tBTCUSD")
```

### Setting a custom `sub_id`

The client generates a random `sub_id` for each subscription. \
These values must be unique, as the client uses them to identify subscriptions. \
However, it is possible to force this value by passing a custom `sub_id` to `BfxWebSocketClient::subscribe`:

```python
await bfx.wss.subscribe("candles", key="trade:1m:tBTCUSD", sub_id="507f1f77bcf86cd799439011")
```

## Listening to events

Whenever the WebSocket client receives data, it will emit a specific event. \
Users can either ignore those events or listen for them by registering callback functions. \
These callback functions can also be asynchronous; in fact the client fully supports coroutines ([`asyncio`](https://docs.python.org/3/library/asyncio.html)).

To add a listener for a specific event, users can use the decorator `BfxWebSocketClient::on`:
```python
@bfx.wss.on("candles_update")
def on_candles_update(sub: subscriptions.Candles, candle: Candle):
    print(f"Candle update for key <{sub['key']}>: {candle}")
```

The same can be done without using decorators:
```python
bfx.wss.on("candles_update", callback=on_candles_update)
```

You can pass any number of events to register for the same callback function:
```python
bfx.wss.on("t_ticker_update", "f_ticker_update", callback=on_ticker_update)
```

## Events

### `open`:

When the connection with the server is established, the client will emit the `open` event. \
This is the right place for all bootstrap activities, including subscribing to public channels.

```python
@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe(Channel.TICKER, symbol="tBTCUSD")
```

### `authenticated`:

If authentication succeeds, the client will emit the `authenticated` event. \
All operations that require authentication must be performed after the emission of this event. \
The `data` argument contains information regarding the authentication, such as the `userId`, the `auth_id`, etc...

```python
@bfx.wss.on("authenticated")
def on_authenticated(data: Dict[str, Any]):
    print(f"Successful login for user <{data['userId']}>.)
```

## Sending custom notifications

**Sending custom notifications requires user authentication.**

Users can send custom notifications using `BfxWebSocketClient::notify`:
```python
await bfx.wss.notify({ "foo": 1 })
```

The server broadcasts custom notifications to each of its clients:
```python
@bfx.wss.on("notification")
def on_notification(notification: Notification[Any]):
    print(notification.data) # { "foo": 1 }
```

## Handling reconnections in case of network failure

In case of network failure, the client will keep waiting until it is able to restore the connection with the server.

The client will try to reconnect with exponential backoff; the backoff delay starts at three seconds and increases up to one minute.

After a successful reconnection attempt, the client will emit the `reconnection` event.

This event accepts two arguments: \
`attemps` (`int`) which is the number of reconnection attempts (including the successful one), \
`timedelta` (`datetime.timedelta`) which contains the amount of time the client has been down.

Users can use this event for a variety of things, such as sending a notification if the client has been down for too long:
```python
@bfx.wss.on("reconnection")
async def on_reconnection(attempts: int, timedelta: datetime.timedelta):
    if timedelta.total_seconds() >= 60 * 60: # 60s * 60s = 3600s = 1h
        await bfx.wss.notify(f"The client has been down for {timedelta}.")
```

---

# Building the source code

## Testing (with unittest)

## Linting the project with pylint

## Using mypy to ensure correct type-hinting

---

# How to contribute

## License
This project is released under the `Apache License 2.0`.

The complete license can be found here: https://www.apache.org/licenses/LICENSE-2.0.
