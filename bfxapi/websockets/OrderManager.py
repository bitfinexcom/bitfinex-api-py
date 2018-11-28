import time
import asyncio

from ..utils.CustomLogger import CustomLogger
from ..models import Order, Trade

class OrderManager:

  def __init__(self, bfxapi, logLevel='INFO'):
    self.bfxapi = bfxapi
    self.pending_orders = {}
    self.pending_callbacks = {}
    self.closed_orders = {}
    self.open_orders = {}
    self.logger = CustomLogger('BfxOrderManager', logLevel=logLevel)

  def get_open_orders(self):
    return list(self.open_orders.values())

  def get_closed_orders(self):
    return list(self.closed_orders.values())

  def get_pending_orders(self):
    return list(self.pending_orders.values())

  async def _confirm_order(self, order, trade):
    '''
    Called once when we first recieve infomation back from the bitfinex api
    that the order has been accepted.
    '''
    if order.cId in self.pending_orders:
      if self.pending_callbacks[order.cId][0]:
        # call onComplete callback
        await self.pending_callbacks[order.cId][0](order, trade)
      order.set_confirmed()
      # remove from pending orders list
      del self.pending_orders[order.cId]
      del self.pending_callbacks[order.cId]
      self.bfxapi._emit('order_confirmed', order, trade)

  async def confirm_order_closed(self, raw_ws_data):
    # order created and executed
    # [0,"oc",[1151349678,null,1542203391995,"tBTCUSD",1542203389940,1542203389966,0,0.1,
    # "EXCHANGE MARKET",null,null,null,0,"EXECUTED @ 18922.0(0.03299997): was PARTIALLY FILLED 
    # @ 18909.0(0.06700003)",null,null,18909,18913.2899961,0,0,null,null,null,0,0,null,null,null,
    # "API>BFX",null,null,null]]
    order = Order(self.bfxapi, raw_ws_data[2])
    trade = Trade(order)
    order.set_open_state(False)
    if order.id in self.open_orders:
      del self.open_orders[order.id]
    await self._confirm_order(order, trade)
    self.logger.info("Order closed: {} {}".format(order.symbol, order.status))
    self.bfxapi._emit('order_closed', order, trade)

  async def build_from_order_snapshot(self, raw_ws_data):
    '''
    Rebuild the user orderbook based on an incoming snapshot
    '''
    osData = raw_ws_data[2]
    self.open_orders = {}
    for raw_order in osData:
      order = Order(self.bfxapi, raw_order)
      trade = Trade(order)
      order.set_open_state(True)
      self.open_orders[order.id] = order
      # await self._confirm_order(order, trade)
    self.bfxapi._emit('order_snapshot', self.open_orders)

  async def confirm_order_update(self, raw_ws_data):
    # order created but partially filled
    # [0, 'ou', [1151351581, None, 1542629457873, 'tBTCUSD', 1542629458071, 
    # 1542629458189, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE', 
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX', 
    # None, None, None]]
    order = Order(self.bfxapi, raw_ws_data[2])
    order.set_open_state(True)
    trade = Trade(order)
    self.open_orders[order.id] = order
    await self._confirm_order(order, trade)
    self.logger.info("Order update: {} {}".format(order, trade))
    self.bfxapi._emit('order_update', order, trade)

  async def confirm_order_new(self, raw_ws_data):
    # order created but not executed /  created but partially filled
    # [0, 'on', [1151351563, None, 1542624024383, 'tBTCUSD', 1542624024596,
    # 1542624024617, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE',
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX',
    # None, None, None]]
    order = Order(self.bfxapi, raw_ws_data[2])
    order.set_open_state(True)
    trade = Trade(order)
    self.open_orders[order.id] = order
    await self._confirm_order(order, trade)
    self.logger.info("Order new: {} {}".format(order, trade))
    self.bfxapi._emit('order_new', order, trade)

  def _gen_unqiue_cid(self):
    return int(round(time.time() * 1000))

  async def submit_order(self, symbol, price, amount, market_type,
      hidden=False, onComplete=None, onError=None, *args, **kwargs):
    cId = self._gen_unqiue_cid()
    # send order over websocket
    payload = {
      "cid": cId,
      "type": str(market_type),
      "symbol": symbol,
      "amount": str(amount),
      "price": str(price)
    }
    self.pending_orders[cId] = payload
    self.pending_callbacks[cId] = (onComplete, onError)
    await self.bfxapi._send_auth_command('on', payload)
    self.logger.info("Order cid={} ({} {} @ {}) dispatched".format(
      cId, symbol, amount, price))

  async def update_order(self, orderId, *args, onComplete=None, onError=None, **kwargs):
    if orderId not in self.open_orders:
      raise Exception("Order id={} is not open".format(orderId))
    order = self.open_orders[orderId]
    self.pending_callbacks[order.cId] = (onComplete, onError)
    await order.update(*args, **kwargs)
    self.logger.info("Update Order order_id={} dispatched".format(orderId))

  async def close_order(self, orderId, onComplete=None, onError=None):
    if orderId not in self.open_orders:
      raise Exception("Order id={} is not open".format(orderId))
    order = self.open_orders[orderId]
    self.pending_callbacks[order.cId] = (onComplete, onError)
    await order.cancel()
    self.logger.info("Order cancel order_id={} dispatched".format(orderId))

  async def close_all_orders(self):
    ids = [self.open_orders[x].id for x in self.open_orders]
    await self.close_order_multi(ids)

  async def close_order_multi(self, orderIds):
    task_batch = []
    for oid in orderIds:
      task_batch += [
        asyncio.ensure_future(self.open_orders[oid].close())
      ]
    await asyncio.wait(*[ task_batch ])
