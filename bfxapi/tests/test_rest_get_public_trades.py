import asyncio
import concurrent.futures
from bfxapi import Client

bfx = Client(logLevel='DEBUG')

async def run():
    start = 1617519600000
    candles = await bfx.rest.get_public_candles(start=start, symbol='tBTCUSD', end=None, tf='1h', sort=1, limit=1)
    candle = candles[0]
    price = candle[1]
    assert price == 57394.61698309

    orders_ids = []
    trades = await bfx.rest.get_public_trades(start=1617519600000, limit=5, symbol='tBTCUSD', end=None, sort=1)
    print(trades)
    for trade in trades:
        orders_ids.append(trade[0])
    assert orders_ids == [657815316, 657815314, 657815312, 657815308, 657815304]

    # check that strictly decreasing order id condition is always respected
    # check that not increasing timestamp condition is always respected
    orders_ids = []
    timestamps = []
    trades = await bfx.rest.get_public_trades(start=1617519600000, limit=5000, symbol='tLEOUSD', end=None, sort=1)
    print(trades)
    for trade in trades:
        orders_ids.append(trade[0])
        timestamps.append(trade[1])

    assert not all(x > y for x, y in zip(orders_ids, orders_ids[1:])) is False
    assert not all(x >= y for x, y in zip(orders_ids, orders_ids[1:])) is False

def test_get_public_trades():
    t = asyncio.ensure_future(run())
    asyncio.get_event_loop().run_until_complete(t)
