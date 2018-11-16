import sys
import time
sys.path.append('../')

from bfxapi.websockets.DataServerWebsocket import DataServerWebsocket

ws = DataServerWebsocket(
  symbol='tBTCUSD',
  host='ws://localhost:8899'
)

@ws.on('new_candle')
def candle(candle):
  print ("Backtest candle: {}".format(candle))

@ws.on('new_trade')
def trade(trade):
  print ("Backtest trade: {}".format(trade))

@ws.on('done')
def finish():
  print ("Backtest complete!")

now = int(round(time.time() * 1000))
then = now - (1000 * 60 * 60 * 24 * 2) # 2 days ago
ws.run(then, now)
