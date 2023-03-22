# bitfinex-api-py (v3-beta)

Official implementation of the [Bitfinex APIs (V2)](https://docs.bitfinex.com/docs) for `Python 3.8+`.

> DISCLAIMER:</br>
Production use of v3.0.0b1 (and all future beta versions) is HIGHLY discouraged.</br>
Beta versions should not be used in applications which require user authentication.</br>
Provide your API-KEY/API-SECRET, and manage your account and funds at your own risk.</br>

### Features
- User-friendly implementations for 75+ public and authenticated REST endpoints.
    * A complete list of available REST endpoints can be found [here](https://docs.bitfinex.com/reference).
- New WebSocket client to ensure fast, secure and persistent connections.
    * Support for all public channels + authenticated events and inputs (a list can be found [here](https://docs.bitfinex.com/docs/ws-public)).
    * Automatic reconnection system in case of network fail (both client and server side).
        - The WebSocket client logs every reconnection failure, success and attempt (as well as other events).
    * Connection multiplexing to allow subscribing to a large number of public channels (without affecting performances).
        - The WebSocket server sets a limit of 25 subscriptions per connection, connection multiplexing allows the WebSocket client to bypass this limit.
- Full type-hinting and type-checking support with [`mypy`](https://github.com/python/mypy). 
    * This allow text editors to show helpful hints about the value of a variable:</br>
      ![example](https://i.imgur.com/aDjapcN.png "Type-hinting example on a random code snippet")
---

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Getting started with the WebSocket client](#getting-started-with-the-websocket-client)
    * [Authentication with API-KEY and API-SECRET](#authentication-with-api-key-and-api-secret)
    * [Configure the WebSocket client logger](#configure-the-websocket-client-logger)
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
Otherwise, to install a specific beta version:
```bash
python3 -m pip install bitfinex-api-py==3.0.0b1
```

## Basic usage

## Getting started with the WebSocket client

### Authentication with API-KEY and API-SECRET

### Configure the WebSocket client logger

## Building the source code

### Testing (with unittest)

### Linting the project with pylint

### Using mypy to ensure correct type-hinting

## How to contribute

### License
This project is released under the `Apache License 2.0`.</br>
The complete license can be found here: https://www.apache.org/licenses/LICENSE-2.0.
