import asyncio
import aiohttp
import time
import json

from ..utils.CustomLogger import CustomLogger

class BfxRest:

  def __init__(self, API_KEY, API_SECRET, host='https://api.bitfinex.com/v2', loop=None,
      logLevel='INFO', *args, **kwargs):
    self.loop = loop or asyncio.get_event_loop()
    self.host = host
    self.logger = CustomLogger('BfxRest', logLevel=logLevel)

  async def fetch(self, endpoint):
    url = '{}/{}'.format(self.host, endpoint)
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        text =  await resp.text()
        if resp.status is not 200:
          raise Exception('Unable to seed trades. Received status {} - {}'
            .format(resp.status, text))
        return json.loads(text)

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
