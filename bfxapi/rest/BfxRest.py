import asyncio
import aiohttp
import time
import json

from ..utils.CustomLogger import CustomLogger
from ..utils.auth import generate_auth_headers
from ..models import Wallet, Order, Position, Trade

class BfxRest:

  def __init__(self, API_KEY, API_SECRET, host='https://api.bitfinex.com/v2', loop=None,
      logLevel='INFO', *args, **kwargs):
    self.loop = loop or asyncio.get_event_loop()
    self.API_KEY = API_KEY
    self.API_SECRET = API_SECRET
    self.host = host
    self.logger = CustomLogger('BfxRest', logLevel=logLevel)

  async def fetch(self, endpoint, params=""):
    url = '{}/{}{}'.format(self.host, endpoint, params)
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        text =  await resp.text()
        if resp.status is not 200:
          raise Exception('GET {} failed with status {} - {}'
            .format(url, resp.status, text))
        return await resp.json()

  async def post(self, endpoint, data={}, params=""):
    url = '{}/{}'.format(self.host, endpoint)
    sData = json.dumps(data)
    headers = generate_auth_headers(
      self.API_KEY, self.API_SECRET, endpoint, sData)
    headers["content-type"] = "application/json"
    async with aiohttp.ClientSession() as session:
      async with session.post(url + params, headers=headers, data=sData) as resp:
        text = await resp.text()
        if resp.status is not 200:
          raise Exception('POST {} failed with status {} - {}'
            .format(url, resp.status, text))
        return await resp.json()

  ##################################################
  #                     Public                     #
  ##################################################

  async def get_seed_candles(self, symbol):
    endpoint = 'candles/trade:1m:{}/hist?limit=5000&_bfx=1'.format(symbol)
    time_difference = (1000 * 60) * 5000
    # get now to the nearest min
    now = int(round((time.time() // 60 * 60) * 1000))
    task_batch = []
    for x in range(0, 10):
      start = x * time_difference
      end = now - (x * time_difference) - time_difference
      e2 = endpoint + '&start={}&end={}'.format(start, end)
      task_batch += [asyncio.ensure_future(self.fetch(e2))]
    self.logger.info("Downloading seed candles from Bitfinex...")
    # call all fetch requests async
    done, _ = await asyncio.wait(*[ task_batch ])
    candles = []
    for task in done:
      candles += task.result()
    candles.sort(key=lambda x: x[0], reverse=True)
    self.logger.info("Downloaded {} candles.".format(len(candles)))
    return candles

  async def get_public_candles(self, symbol, start, end, section='hist',
    tf='1m', limit="100", sort=-1):
    endpoint = "candles/trade:{}:{}/{}".format(tf, symbol, section)
    params = "?start={}&end={}&limit={}&sort={}".format(start, end, limit, sort)
    candles = await self.fetch(endpoint, params=params)
    return candles

  async def get_public_trades(self, symbol, start, end, limit="100", sort=-1):
    endpoint = "trades/{}/hist".format(symbol)
    params = "?start={}&end={}&limit={}&sort={}".format(start, end, limit, sort)
    trades = await self.fetch(endpoint, params=params)
    return trades

  async def get_public_books(self, symbol, precision="P0", length=25):
    endpoint = "book/{}/{}".format(symbol, precision)
    params = "?len={}".format(length)
    books = await self.fetch(endpoint, params)
    return books

  async def get_public_ticker(self, symbol):
    endpoint = "ticker/{}".format(symbol)
    ticker = await self.fetch(endpoint)
    return ticker

  ##################################################
  #                 Authenticated                  #
  ##################################################

  async def get_wallets(self):
    endpoint = "auth/r/wallets"
    raw_wallets = await self.post(endpoint)
    return [ Wallet(*rw[:4]) for rw in raw_wallets ]

  async def get_active_orders(self, symbol):
    endpoint = "auth/r/orders/{}".format(symbol)
    raw_orders = await self.post(endpoint)
    return [ Order.from_raw_order(ro) for ro in raw_orders ]

  async def get_order_history(self, symbol, start, end, limit=25, sort=-1):
    endpoint = "auth/r/orders/{}/hist".format(symbol)
    params = "?start={}&end={}&limit={}&sort={}".format(start, end, limit, sort)
    raw_orders = await self.post(endpoint, params=params)
    return [ Order.from_raw_order(ro) for ro in raw_orders ]

  async def get_active_position(self):
    endpoint = "auth/r/positions"
    raw_positions = await self.post(endpoint)
    return [ Position.from_raw_rest_position(rp) for rp in raw_positions ]

  async def get_trades(self, symbol, start, end, limit=25):
    endpoint = "auth/r/trades/{}/hist".format(symbol)
    params = "?start={}&end={}&limit={}".format(start, end, limit)
    raw_trades = await self.post(endpoint, params=params)
    return [ Trade.from_raw_rest_trade(rt) for rt in raw_trades ]
