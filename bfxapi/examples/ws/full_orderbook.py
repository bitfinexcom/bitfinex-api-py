import os
import sys
import time
from collections import OrderedDict
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  manageOrderBooks=True
)

class OrderBook:
  def __init__(self, snapshot):
    self.bids = OrderedDict()
    self.asks = OrderedDict()
    self.load(snapshot)

  def load(self, snapshot):
    for record in snapshot:
      if record[2] >= 0:
        self.bids[record[0]] = {
          'count': record[1],
          'amount': record[2]
        }
      else:
        self.asks[record[0]] = {
          'count': record[1],
          'amount': record[2]
        }

  def update(self, record):
    # count is 0
    if record[1] == 0:
      if record[2] == 1:
        # remove from bids
        del self.bids[record[0]]
      elif record[2] == -1:
        # remove from asks
        del self.asks[record[0]]
    elif record[1] > 0:
      if record[2] > 0:
        # update bids
        if record[0] not in self.bids:
          self.bids[record[0]] = {}
        self.bids[record[0]]['count'] = record[1]
        self.bids[record[0]]['amount'] = record[2]
      elif record[2] < 0:
        # update asks
        if record[0] not in self.asks:
          self.asks[record[0]] = {}
        self.asks[record[0]]['count'] = record[1]
        self.asks[record[0]]['amount'] = record[2]

obs = {}

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('order_book_update')
def log_update(data):
  obs[data['symbol']].update(data['data'])

@bfx.ws.on('order_book_snapshot')
def log_snapshot(data):
  obs[data['symbol']] = OrderBook(data['data'])

async def start():
  await bfx.ws.subscribe('book', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()

for n in range(0, 10):
  time.sleep(2)
  for key in obs:
    print(f"Printing {key} orderbook...")
    print(f"{obs[key].bids}\n")
    print(f"{obs[key].asks}\n")
