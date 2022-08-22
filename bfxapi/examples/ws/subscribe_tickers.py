import sys
sys.path.append('../../../')

from bfxapi import Client, PUB_WS_HOST, PUB_REST_HOST

# Retrieving tickers requires public hosts
bfx = Client(
  logLevel='DEBUG',
  ws_host=PUB_WS_HOST,
  rest_host=PUB_REST_HOST
)

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('new_funding_ticker')
def log_ticker(ticker):
  print ("New ticker: {}".format(ticker))

async def start():
  await bfx.ws.subscribe('ticker', 'fUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
