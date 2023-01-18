# python -c "from examples.rest.get_public_data import *"

import time

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST
)

now = int(round(time.time() * 1000))


def log_historical_candles():
    candles = bfx.rest.public.get_candles_hist(start=0, end=now, resource='trade:1m:tBTCUSD')
    print("Candles:")
    [print(c) for c in candles]


def log_historical_trades():
    trades = bfx.rest.public.get_t_trades(pair='tBTCUSD', start=0, end=now)
    print("Trades:")
    [print(t) for t in trades]


def log_books():
    orders = bfx.rest.public.get_t_book(pair='BTCUSD', precision='P0')
    print("Order book:")
    [print(o) for o in orders]


def log_tickers():
    tickers = bfx.rest.public.get_t_tickers(pairs=['BTCUSD'])
    print("Tickers:")
    print(tickers)


def log_derivative_status():
    status = bfx.rest.public.get_derivatives_status('ALL')
    print("Deriv status:")
    print(status)


def run():
    log_historical_candles()
    log_historical_trades()
    log_books()
    log_tickers()
    log_derivative_status()


run()