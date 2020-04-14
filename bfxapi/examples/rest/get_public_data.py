import os
import sys
import asyncio
import time
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG',
)

now = int(round(time.time() * 1000))
then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago

async def log_historical_candles():
  candles = await bfx.rest.get_public_candles('tBTCUSD', 0, then)
  print ("Candles:")
  [ print (c) for c in candles ]

async def log_historical_trades():
  trades = await bfx.rest.get_public_trades('tBTCUSD', 0, then)
  print ("Trades:")
  [ print (t) for t in trades ]

async def log_books():
  orders = await bfx.rest.get_public_books('tBTCUSD')
  print ("Order book:")
  [ print (o) for o in orders ]

async def log_ticker():
  ticker = await bfx.rest.get_public_ticker('tBTCUSD')
  print ("Ticker:")
  print (ticker)

async def log_mul_tickers():
  tickers = await bfx.rest.get_public_tickers(['tBTCUSD', 'tETHBTC'])
  print ("Tickers:")
  print (tickers)

async def log_derivative_status():
  status = await bfx.rest.get_derivative_status('tBTCF0:USTF0')
  print ("Deriv status:")
  print (status)

async def run():
  await log_historical_candles()
  await log_historical_trades()
  await log_books()
  await log_ticker()
  await log_mul_tickers()
  await log_derivative_status()
  
t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
