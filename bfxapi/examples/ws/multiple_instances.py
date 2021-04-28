"""
This is an example of how is it possible to spawn multiple
bfx ws instances to comply to the open subscriptions number contraint (max. 25)

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
    tickers = ["AAABBB", "AAVE:USD", "AAVE:UST", "ADABTC", "ADAUSD", "ADAUST", "ALBT:USD", "ALBT:UST", "ALGBTC",
               "ALGUSD", "ALGUST", "AMPBTC", "AMPUSD", "AMPUST", "ANTBTC", "ANTETH", "ANTUSD", "ATOBTC", "ATOETH",
               "ATOUSD", "AVAX:USD", "AVAX:UST", "B21X:USD", "B21X:UST", "BALUSD", "BALUST", "BAND:USD", "BAND:UST",
               "BATBTC", "BATETH", "BATUSD", "BCHABC:USD", "BCHN:USD", "BEST:USD", "BFTUSD", "BMIUSD", "BMIUST",
               "BNTUSD", "BOSON:USD", "BOSON:UST", "BSVBTC", "BSVUSD", "BTC:CNHT", "BTCEUR", "BTCGBP", "BTCJPY",
               "BTCUSD", "BTCUST", "BTCXCH", "BTGBTC", "BTGUSD", "BTSE:USD", "BTTUSD", "CELUSD", "CELUST", "CHZUSD",
               "CHZUST", "CLOUSD", "CNH:CNHT", "COMP:USD", "COMP:UST", "CTKUSD", "CTKUST", "DAIBTC", "DAIETH", "DAIUSD",
               "DAPP:USD", "DAPP:UST", "DATBTC", "DATUSD", "DGBUSD", "DGXUSD", "DOGBTC", "DOGE:USD", "DOGE:UST",
               "DOGUSD", "DOGUST", "DOTBTC", "DOTUSD", "DOTUST", "DSHBTC", "DSHUSD", "DUSK:BTC", "DUSK:USD", "EDOBTC",
               "EDOETH", "EDOUSD", "EGLD:USD", "EGLD:UST", "ENJUSD", "EOSBTC", "EOSDT:USD", "EOSDT:UST", "EOSETH",
               "EOSEUR", "EOSGBP", "EOSJPY", "EOSUSD", "EOSUST", "ESSUSD", "ETCBTC", "ETCUSD", "ETH2X:ETH", "ETH2X:USD",
               "ETH2X:UST", "ETHBTC", "ETHEUR", "ETHGBP", "ETHJPY", "ETHUSD", "ETHUST", "ETPBTC", "ETPETH", "ETPUSD",
               "EUSBTC", "EUSUSD", "EUTEUR", "EUTUSD", "EUTUST", "EXRD:BTC", "EXRD:USD", "FETUSD", "FETUST", "FILUSD",
               "FILUST", "FTTUSD", "FTTUST", "FUNUSD", "GNOUSD", "GNTUSD", "GOTEUR", "GOTUSD", "GTXUSD", "GTXUST",
               "HEZUSD", "HEZUST", "ICEUSD", "IOTBTC", "IOTETH", "IOTEUR", "IOTGBP", "IOTJPY", "IOTUSD", "IQXUSD",
               "IQXUST", "JSTBTC", "JSTUSD", "JSTUST", "KANUSD", "KANUST", "KNCBTC", "KNCUSD", "KSMUSD", "KSMUST",
               "LEOBTC", "LEOEOS", "LEOETH", "LEOUSD", "LEOUST", "LINK:USD", "LINK:UST", "LRCUSD", "LTCBTC", "LTCUSD",
               "LTCUST", "LUNA:USD", "LUNA:UST", "LYMUSD", "MKRUSD", "MLNUSD", "MNABTC", "MNAUSD", "MOBUSD", "MOBUST",
               "NEAR:USD", "NEAR:UST", "NECUSD", "NEOBTC", "NEOETH", "NEOEUR", "NEOGBP", "NEOJPY", "NEOUSD", "NUTUSD",
               "ODEUSD", "OMGBTC", "OMGETH", "OMGUSD", "OMNBTC", "OMNUSD", "ORSUSD", "PASUSD", "PAXUSD", "PAXUST",
               "PLUUSD", "PNKETH", "PNKUSD", "POAUSD", "QSHUSD", "QTMBTC", "QTMUSD", "RBTBTC", "RBTUSD", "REPBTC",
               "REPUSD", "REQUSD", "RINGX:USD", "RRBUSD", "RRBUST", "RRTUSD", "SANBTC", "SANETH", "SANUSD", "SNGUSD",
               "SNTUSD", "SNXUSD", "SNXUST", "SOLUSD", "SOLUST", "STJUSD", "SUKU:USD", "SUKU:UST", "SUNUSD", "SUNUST",
               "SUSHI:USD", "SUSHI:UST", "TESTBTC:TESTUSD", "TESTBTC:TESTUSDT", "TRXBTC", "TRXETH", "TRXEUR", "TRXUSD",
               "TSDUSD", "TSDUST", "UDCUSD", "UDCUST", "UNIUSD", "UNIUST", "UOPUSD", "UOPUST", "UOSBTC", "UOSUSD",
               "USKUSD", "UST:CNHT", "USTUSD", "UTKUSD", "VEEUSD", "VETBTC", "VETUSD", "VSYBTC", "VSYUSD", "WAXUSD",
               "WBTUSD", "XAUT:BTC", "XAUT:USD", "XAUT:UST", "XCHUSD", "XDCUSD", "XDCUST", "XLMBTC", "XLMETH", "XLMUSD",
               "XLMUST", "XMRBTC", "XMRUSD", "XMRUST", "XRAUSD", "XRPBTC", "XRPUSD", "XRPUST", "XSNUSD", "XTZBTC",
               "XTZUSD", "XVGUSD", "YFIUSD", "YFIUST", "YGGUSD", "YYWUSD", "ZBTUSD", "ZCNUSD", "ZECBTC", "ZECUSD",
               "ZILBTC", "ZILUSD", "ZRXBTC", "ZRXETH", "ZRXUSD"]
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
        to_sub = [f"t{ticker}" for ticker in get_random_list_of_tickers() if ticker not in subbed_tickers]
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

        to_unsub = [f"t{ticker}" for ticker in subbed_tickers if ticker in get_random_list_of_tickers()]
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