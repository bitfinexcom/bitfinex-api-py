"""Tests for REST API
"""
import logging
from datetime import datetime
from bfxapi.rest.bfx_rest import BfxRest
import asyncio

# Set auth params
API_KEY = 'api-key'
API_SECRET = 'api-secret'

# v2 REST api
bfx = BfxRest(API_KEY, API_SECRET, loop=None, logLevel='DEBUG', parse_float=float)


def test_get_candles():
    start = 1000 * datetime(2021, 11, 5).timestamp()
    end = 1000 * datetime(2021, 11, 5, 23).timestamp()
    
    # bfxapi returns coroutine objects, which needs to handled later
    candles = bfx.get_public_candles(
        'tBTCUSD',
        start,
        end,
        section='hist',
        tf='1m',
        limit='100',
        sort=-1
    )

    print("\nCandles:")
    print(asyncio.run(candles))


def test_get_active_positions():
    active_positions = bfx.get_active_position()

    print("\nActive positions:")
    print(asyncio.run(active_positions))


def test_submit_order():
    symbol = 'tTESTBTC:TESTUSD'
    price = 25000
    amount = 0.1
        
    submit_order = bfx.submit_order(
        symbol,
        price,
        amount,
        market_type='EXCHANGE LIMIT',
        hidden=False,
        price_trailing=None,
        price_aux_limit=None,
        oco_stop_price=None,
        close=False,
        reduce_only=False,
        post_only=False,
        oco=False,
        aff_code=None,
        time_in_force=None,
        leverage=None,
        gid=None
    )

    res = asyncio.run(submit_order)
    print("\Create order:")
    print(res.notify_info[0])


def test_submit_cancel_order():
    order_id = 77921347342
    
    cancel_order = bfx.submit_cancel_order(order_id)

    res = asyncio.run(cancel_order)
    print("\Cancel order:")
    print(res)


def test_update_order():
    # order_id = 77921374472    # Active order
    order_id = 77921347342    # Already cancelled order
    
    update_order = bfx.submit_update_order(order_id)

    res = asyncio.run(update_order)
    print("\nUpdate order:")
    print(res)


def test_get_active_orders():
    get_active_orders = bfx.get_active_orders('tTESTBTC:TESTUSD')

    res = asyncio.run(get_active_orders)
    print("\nActive orders:")
    print(res)


def test_get_all_active_orders():
    get_all_active_orders = bfx.get_active_orders()

    res = asyncio.run(get_all_active_orders)
    print("\nActive orders ({} orders):".format(len(res)))
    print(res)


def test_get_order_history():
    start = 1000 * datetime(2021, 11, 5).timestamp()
    end = 1000 * datetime(2021, 11, 5, 23).timestamp()
    
    order_history = bfx.get_order_history('tTESTBTC:TESTUSD', start, end, limit=1000)

    res = asyncio.run(order_history)
    print("\nOrder history:")
    print("{} orders".format(len(res)))
    print(res)
    print("Order IDs:")
    print([order.id for order in res])


def test_get_order_history_ids():
    # order_id = 77921374472    # Active order
    # order_id = 77921347342    # Already cancelled order
    order_ids = [77769182836, 77769177293, 77769082712, 77769073775]    # Saved from above run
    start = 1000 * datetime(2021, 11, 5).timestamp()
    end = 1000 * datetime(2021, 11, 5, 23).timestamp()
    
    order_history = bfx.get_order_history('tTESTBTC:TESTUSD', start, end, ids=order_ids)

    res = asyncio.run(order_history)
    print("\nOrder history:")
    print(res)


def test_get_all_order_history():
    order_history = bfx.get_order_history()

    res = asyncio.run(order_history)
    print("\nOrder history ({} orders):".format(len(res)))
    print(res)


def test_get_all_order_history_ids():
    order_ids = [77769182836, 77769177293, 77769082712, 77769073775]    # Saved from above run
    order_history = bfx.get_all_order_history(ids=order_ids)

    res = asyncio.run(order_history)
    print("\nOrder history ({} orders):".format(len(res)))
    print(res)


def test_get_trades():
    start = 1000 * datetime(2021, 11, 5).timestamp()
    end = 1000 * datetime(2021, 11, 5, 23).timestamp()
    trades = bfx.get_trades(symbol='tTESTBTC:TESTUSD', start=start, end=end, limit=1000)
    res = asyncio.run(trades)
    print("\Trades ({} trades):".format(len(res)))
    print(res)


def test_get_trades_all():
    trades = bfx.get_trades(limit=1000)
    res = asyncio.run(trades)
    print("\Trades ({} trades):".format(len(res)))
    print(res)


def test_get_active_positions():
    active_positions = bfx.get_active_position()
    res = asyncio.run(active_positions)
    print("\Active positions ({} positions):".format(len(res)))
    print(res)
    
    
if __name__ == "__main__":
    logging.basicConfig(level='DEBUG')
    
    test_get_all_active_orders()
    test_get_all_order_history()
    # test_get_all_order_history_ids()
    # test_get_trades()
    # test_get_trades_all()
    # test_get_active_positions()
