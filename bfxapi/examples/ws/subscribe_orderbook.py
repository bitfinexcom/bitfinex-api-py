import os
import sys
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG',
  # Verifies that the local orderbook is up to date
  # with the bitfinex servers
  manageOrderBooks=True
)

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('order_book_update')
def log_update(data):
  print ("Book update: {}".format(data))

@bfx.ws.on('order_book_snapshot')
def log_snapshot(data):
  print ("Initial book: {}".format(data))

async def start():
  await bfx.ws.subscribe('book', 'tBTCUSD')
  # bfx.ws.subscribe('book', 'tETHUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
