# bitfinex-api-py

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bitfinex-api-py)](https://pypi.org/project/bitfinex-api-py/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub Action](https://github.com/bitfinexcom/bitfinex-api-py/actions/workflows/build.yml/badge.svg)

Official implementation of the [Bitfinex APIs (V2)](https://docs.bitfinex.com/docs) for `Python 3.8+`.

### Features

* Support for 75+ REST endpoints (a list of available endpoints can be found [here](https://docs.bitfinex.com/reference))
* New WebSocket client to ensure fast, secure and persistent connections
* Full support for Bitfinex notifications (including custom notifications)
* Native support for type hinting and type checking with [`mypy`](https://github.com/python/mypy)

## Installation

```console
python3 -m pip install bitfinex-api-py
```

---

# Quickstart

```python
from bfxapi import Client, REST_HOST

from bfxapi.types import Notification, Order

bfx = Client(
    rest_host=REST_HOST,
    api_key="<YOUR BFX API-KEY>",
    api_secret="<YOUR BFX API-SECRET>"
)

notification: Notification[Order] = bfx.rest.auth.submit_order(
    type="EXCHANGE LIMIT", symbol="tBTCUSD", amount=0.165212, price=30264.0)

order: Order = notification.data

if notification.status == "SUCCESS":
    print(f"Successful new order for {order.symbol} at {order.price}$.")

if notification.status == "ERROR":
    raise Exception(f"Something went wrong: {notification.text}")
```

## Authenticating in your account

To authenticate in your account, you must provide a valid API-KEY and API-SECRET:
```python
bfx = Client(
    [...],
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)
```

### Warning

Remember to not share your API-KEYs and API-SECRETs with anyone. \
Everyone who owns one of your API-KEYs and API-SECRETs will have full access to your account. \
We suggest saving your credentials in a local `.env` file and accessing them as environment variables.

_Revoke your API-KEYs and API-SECRETs immediately if you think they might have been stolen._

> **NOTE:** A guide on how to create, edit and revoke API-KEYs and API-SECRETs can be found [here](https://support.bitfinex.com/hc/en-us/articles/115003363429-How-to-create-and-revoke-a-Bitfinex-API-Key).

## Next

* [WebSocket client documentation](#websocket-client-documentation)
    - [Advanced features](#advanced-features)
    - [Examples](#examples)
* [How to contribute](#how-to-contribute)

---

# WebSocket client documentation

1. [Instantiating the client](#instantiating-the-client)
    * [Authentication](#authentication)
2. [Running the client](#running-the-client)
    * [Closing the connection](#closing-the-connection)
3. [Subscribing to public channels](#subscribing-to-public-channels)
    * [Unsubscribing from a public channel](#unsubscribing-from-a-public-channel)
    * [Setting a custom `sub_id`](#setting-a-custom-sub_id)
4. [Listening to events](#listening-to-events)

### Advanced features
* [Using custom notifications](#using-custom-notifications)

### Examples
* [Creating a new order](#creating-a-new-order)

## Instantiating the client

```python
bfx = Client(wss_host=PUB_WSS_HOST)
```

`Client::wss` contains an instance of `BfxWebSocketClient` (core implementation of the WebSocket client). \
The `wss_host` argument is used to indicate the URL to which the WebSocket client should connect. \
The `bfxapi` package exports 2 constants to quickly set this URL:

Constant | URL | When to use
:--- | :--- | :---
WSS_HOST | wss://api.bitfinex.com/ws/2 | Suitable for all situations, supports authentication.
PUB_WSS_HOST | wss://api-pub.bitfinex.com/ws/2 | For public uses only, doesn't support authentication.

PUB_WSS_HOST is recommended over WSS_HOST for applications that don't require authentication.

> **NOTE:** The `wss_host` parameter is optional, and the default value is WSS_HOST.

### Authentication

To learn how to authenticate in your account, have a look at [Authenticating in your account](#authenticating-in-your-account).

If authentication is successful, the client will emit the `authenticated` event. \
All operations that require authentication will fail if run before the emission of this event. \
The `data` argument contains information about the authentication, such as the `userId`, the `auth_id`, etc...

```python
@bfx.wss.on("authenticated")
def on_authenticated(data: Dict[str, Any]):
    print(f"Successful login for user <{data['userId']}>.")
```

`data` can also be useful for checking if an API-KEY has certain permissions:

```python
@bfx.wss.on("authenticated")
def on_authenticated(data: Dict[str, Any]):
    if not data["caps"]["orders"]["read"]:
        raise Exception("This application requires read permissions on orders.")

    if not data["caps"]["positions"]["write"]:
        raise Exception("This application requires write permissions on positions.")
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

If the client succeeds in connecting to the server, it will emit the `open` event. \
This is the right place for all bootstrap activities, such as subscribing to public channels. \
To learn more about events and public channels, see [Listening to events](#listening-to-events) and [Subscribing to public channels](#subscribing-to-public-channels).

```python
@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe("ticker", symbol="tBTCUSD")
```

### Closing the connection

Users can close the connection with the WebSocket server using `BfxWebSocketClient::close`:
```python
await bfx.wss.close()
```

A custom [close code number](https://www.iana.org/assignments/websocket/websocket.xhtml#close-code-number), along with a verbose reason, can be given as parameters:
```python
await bfx.wss.close(code=1001, reason="Going Away")
```

After closing the connection, the client will emit the `disconnected` event:
```python
@bfx.wss.on("disconnected")
def on_disconnected(code: int, reason: str):
    if code == 1000 or code == 1001:
        print("Closing the connection without errors!")
```

## Subscribing to public channels

Users can subscribe to public channels using `BfxWebSocketClient::subscribe`:
```python
await bfx.wss.subscribe("ticker", symbol="tBTCUSD")
```

On each successful subscription, the client will emit the `subscribed` event:
```python
@bfx.wss.on("subscribed")
def on_subscribed(subscription: subscriptions.Subscription):
    if subscription["channel"] == "ticker":
        print(f"{subscription['symbol']}: {subscription['sub_id']}") # tBTCUSD: f2757df2-7e11-4244-9bb7-a53b7343bef8
```

### Unsubscribing from a public channel

It is possible to unsubscribe from a public channel at any time. \
Unsubscribing from a public channel prevents the client from receiving any more data from it. \
This can be done using `BfxWebSocketClient::unsubscribe`, and passing the `sub_id` of the public channel you want to unsubscribe from:

```python
await bfx.wss.unsubscribe(sub_id="f2757df2-7e11-4244-9bb7-a53b7343bef8")
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

# Advanced features

## Using custom notifications

**Using custom notifications requires user authentication.**

Users can send custom notifications using `BfxWebSocketClient::notify`:
```python
await bfx.wss.notify({ "foo": 1 })
```

Any data can be sent along with a custom notification.

Custom notifications are broadcast by the server on all user's open connections. \
So, each custom notification will be sent to every online client of the current user. \
Whenever a client receives a custom notification, it will emit the `notification` event:
```python
@bfx.wss.on("notification")
def on_notification(notification: Notification[Any]):
    print(notification.data) # { "foo": 1 }
```

# Examples

## Creating a new order

```python
import os

from bfxapi import Client, WSS_HOST

from bfxapi.types import Notification, Order

bfx = Client(
    wss_host=WSS_HOST,
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

@bfx.wss.on("authenticated")
async def on_authenticated(_):
    await bfx.wss.inputs.submit_order(
        type="EXCHANGE LIMIT", symbol="tBTCUSD", amount=0.165212, price=30264.0)

@bfx.wss.on("order_new")
def on_order_new(order: Order):
    print(f"Successful new order for {order.symbol} at {order.price}$.")

@bfx.wss.on("on-req-notification")
def on_notification(notification: Notification[Order]):
    if notification.status == "ERROR":
        raise Exception(f"Something went wrong: {notification.text}")

bfx.wss.run()
```

---

# How to contribute

All contributions are welcome! :D

A guide on how to install and set up `bitfinex-api-py`'s source code can be found [here](#installation-and-setup). \
Before opening any pull requests, please have a look at [Before Opening a PR](#before-opening-a-pr). \
Contributors must uphold the [Contributor Covenant code of conduct](https://github.com/bitfinexcom/bitfinex-api-py/blob/master/CODE_OF_CONDUCT.md).

### Index

1. [Installation and setup](#installation-and-setup)
    * [Cloning the repository](#cloning-the-repository)
    * [Installing the dependencies](#installing-the-dependencies)
    * [Set up the pre-commit hooks (optional)](#set-up-the-pre-commit-hooks-optional)
2. [Before opening a PR](#before-opening-a-pr)
    * [Tip](#tip)
3. [License](#license)

## Installation and setup

A brief guide on how to install and set up the project in your Python 3.8+ environment.

### Cloning the repository

```console
git clone https://github.com/bitfinexcom/bitfinex-api-py.git
```

### Installing the dependencies

```console
python3 -m pip install -r dev-requirements.txt
```

Make sure to install `dev-requirements.txt` (and not `requirements.txt`!). \
`dev-requirements.txt` will install all dependencies in `requirements.txt` plus any development dependency. \
dev-requirements includes [mypy](https://github.com/python/mypy), [black](https://github.com/psf/black), [isort](https://github.com/PyCQA/isort), [flake8](https://github.com/PyCQA/flake8), and [pre-commit](https://github.com/pre-commit/pre-commit) (more on these tools in later chapters).

All done, your Python 3.8+ environment should now be able to run `bitfinex-api-py`'s source code.

### Set up the pre-commit hooks (optional)

**Do not skip this paragraph if you intend to contribute to the project.**

This repository includes a pre-commit configuration file that defines the following hooks:
1. [isort](https://github.com/PyCQA/isort)
2. [black](https://github.com/psf/black)
3. [flake8](https://github.com/PyCQA/flake8)

To set up pre-commit use:
```console
python3 -m pre-commit install
```

These will ensure that isort, black and flake8 are run on each git commit.

[Visit this page to learn more about git hooks and pre-commit.](https://pre-commit.com/#introduction)

#### Manually triggering the pre-commit hooks

You can also manually trigger the execution of all hooks with:
```console
python3 -m pre-commit run --all-files
```

## Before opening a PR

**We won't accept your PR or we'll request changes if the following requirements aren't met.**

Wheter you're submitting a bug fix, a new feature or a documentation change, you should first discuss it in an issue.

You must be able to check off all tasks listed in [PULL_REQUEST_TEMPLATE](https://raw.githubusercontent.com/bitfinexcom/bitfinex-api-py/master/.github/PULL_REQUEST_TEMPLATE.md) before opening a pull request.

### Tip

Setting up the project's pre-commit hooks will help automate this process ([more](#set-up-the-pre-commit-hooks-optional)).

## License

```
Copyright 2023 Bitfinex

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
