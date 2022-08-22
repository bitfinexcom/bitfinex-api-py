import sys
sys.path.append('../../../')

from bfxapi import Client, PUB_WS_HOST, PUB_REST_HOST

bfx = Client(
  logLevel='DEBUG',
  ws_host=PUB_WS_HOST,
  rest_host=PUB_REST_HOST
)

@bfx.ws.on('order_book_snapshot')
async def log_snapshot(data):
  print ("Snapshot: {}".format(data))
  # stop the websocket once a snapshot is received
  await bfx.ws.stop()

async def start():
  await bfx.ws.subscribe('book', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
