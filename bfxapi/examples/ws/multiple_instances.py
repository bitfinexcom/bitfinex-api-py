"""
This is an example of how it is possible to spawn multiple
bfx ws instances to comply with the open subscriptions number constraint (max. 25)

(https://docs.bitfinex.com/docs/requirements-and-limitations)
"""

import sys
sys.path.append('../../../')
import asyncio
import json
from datetime import datetime
from functools import partial
import websockets as ws
from bfxapi import Client
import math
import random

MAX_CHANNELS = 25


def get_random_list_of_tickers():
    tickers = ["FILUST", "FTTUSD", "FTTUST", "FUNUSD", "GNOUSD", "GNTUSD", "GOTEUR", "GOTUSD", "GTXUSD", "ZRXUSD"]
    return random.sample(tickers, 1)


class Instance:
    def __init__(self, _id):
        self.id = _id
        self.bfx = Client(logLevel='INFO')
        self.subscriptions = {'trades': {}, 'ticker': {}}
        self.is_ready = False

    def run(self):
        self.bfx.ws.run()
        self.bfx.ws.on('error', log_error)
        self.bfx.ws.on('new_trade', log_trade)
        self.bfx.ws.on('new_ticker', log_ticker)
        self.bfx.ws.on('subscribed', partial(on_subscribe, self))
        self.bfx.ws.on('unsubscribed', partial(on_unsubscribed, self))
        self.bfx.ws.on('connected', partial(on_connected, self))
        self.bfx.ws.on('stopped', partial(on_stopped, self))

    async def subscribe(self, symbols):
        for symbol in symbols:
            print(f'Subscribing to {symbol} channel')
            await self.bfx.ws.subscribe_ticker(symbol)
            await self.bfx.ws.subscribe_trades(symbol)
            self.subscriptions['trades'][symbol] = None
            self.subscriptions['ticker'][symbol] = None

    async def unsubscribe(self, symbols):
        for symbol in symbols:
            if symbol in self.subscriptions['trades']:
                print(f'Unsubscribing to {symbol} channel')
                trades_ch_id = self.subscriptions['trades'][symbol]
                ticker_ch_id = self.subscriptions['ticker'][symbol]
                if trades_ch_id:
                    await self.bfx.ws.unsubscribe(trades_ch_id)
                else:
                    del self.subscriptions['trades'][symbol]
                if ticker_ch_id:
                    await self.bfx.ws.unsubscribe(ticker_ch_id)
                else:
                    del self.subscriptions['ticker'][symbol]


class Routine:
    is_stopped = False

    def __new__(cls, _loop, _ws, interval=1, start_delay=10):
        instance = super().__new__(cls)
        instance.interval = interval
        instance.start_delay = start_delay
        instance.ws = _ws
        instance.task = _loop.create_task(instance.run())
        return instance.task

    async def run(self):
        await asyncio.sleep(self.start_delay)
        await self.do()
        while True:
            await asyncio.sleep(self.interval)
            await self.do()

    async def do(self):
        subbed_tickers = get_all_subscriptions_tickers()
        print(f'Subscribed tickers: {subbed_tickers}')

        # if ticker is not in subbed tickers, then we subscribe to the channel
        to_sub = [f"t{ticker}" for ticker in get_random_list_of_tickers() if f"t{ticker}" not in subbed_tickers]
        for ticker in to_sub:
            print(f'To subscribe: {ticker}')
            instance = get_available_instance()
            if instance and instance.is_ready:
                print(f'Subscribing on instance {instance.id}')
                await instance.subscribe([ticker])
            else:
                instances_to_create = math.ceil(len(to_sub) / MAX_CHANNELS)
                create_instances(instances_to_create)
                break

        to_unsub = [f"t{ticker}" for ticker in subbed_tickers if f"t{ticker}" in get_random_list_of_tickers()]
        if len(to_unsub) > 0:
            print(f'To unsubscribe: {to_unsub}')
            for instance in instances:
                await instance.unsubscribe(to_unsub)

    def stop(self):
        self.task.cancel()
        self.is_stopped = True


instances = []


def get_all_subscriptions_tickers():
    tickers = []
    for instance in instances:
        for ticker in instance.subscriptions['trades']:
            tickers.append(ticker)
    return tickers


def count_open_channels(instance):
    return len(instance.subscriptions['trades']) + len(instance.subscriptions['ticker'])


def create_instances(instances_to_create):
    for _ in range(0, instances_to_create):
        instance = Instance(len(instances))
        instance.run()
        instances.append(instance)


def get_available_instance():
    for instance in instances:
        if count_open_channels(instance) + 1 <= MAX_CHANNELS:
            return instance
    return None


def log_error(err):
    print("Error: {}".format(err))


def log_trade(trade):
    print(trade)


def log_ticker(ticker):
    print(ticker)


async def on_subscribe(instance, subscription):
    print(f'Subscribed to {subscription.symbol} channel {subscription.channel_name}')
    instance.subscriptions[subscription.channel_name][subscription.symbol] = subscription.chan_id


async def on_unsubscribed(instance, subscription):
    print(f'Unsubscribed to {subscription.symbol} channel {subscription.channel_name}')
    instance.subscriptions[subscription.channel_name][subscription.symbol] = subscription.chan_id
    del instance.subscriptions[subscription.channel_name][subscription.symbol]


async def on_connected(instance):
    print(f"Instance {instance.id} is connected")
    instance.is_ready = True


async def on_stopped(instance):
    print(f"Instance {instance.id} is dead, removing it from instances list")
    instances.pop(instance.id)


def run():
    loop = asyncio.get_event_loop()
    task = Routine(loop, ws, interval=5)
    loop.run_until_complete(task)

run()
