import time

from ..utils.CustomLogger import CustomLogger
from ..models import Order, Trade

class OrderManager:

  def __init__(self, bfxapi, logLevel='INFO'):
    self.bfxapi = bfxapi
    self.pending_orders = {}
    self.confirmed_orders = {}
    self.confirmed_trades = {}
    self.logger = CustomLogger('BfxOrderManager', logLevel=logLevel)

  def get_confirmed_trades(self):
    return list(self.confirmed_trades.values())

  def get_confirmed_orders(self):
    return list(self.confirmed_orders.values())

  def get_pending_orders(self):
    return list(self.pending_orders.values())

  async def _confirm_order(self, order, trade):
    if order.cId in self.pending_orders:
      if self.pending_orders[order.cId][0]:
        # call onComplete callback
        await self.pending_orders[order.cId][0](order, trade)
      # add to confirmed orders list
      order.set_confirmed()
      self.confirmed_orders[order.cId] = order
      self.confirmed_trades[order.cId] = trade
      # remove from pending orders list
      del self.pending_orders[order.cId]
      self.bfxapi._emit('order_confirmed', order, trade)

  async def confirm_order_closed(self, raw_ws_data):
    # order created and executed
    # [0,"oc",[1151349678,null,1542203391995,"tBTCUSD",1542203389940,1542203389966,0,0.1,
    # "EXCHANGE MARKET",null,null,null,0,"EXECUTED @ 18922.0(0.03299997): was PARTIALLY FILLED 
    # @ 18909.0(0.06700003)",null,null,18909,18913.2899961,0,0,null,null,null,0,0,null,null,null,
    # "API>BFX",null,null,null]]
    order = Order(raw_ws_data[2])
    trade = Trade(order)
    self.logger.info("Order closed: {} {}".format(order.symbol, order.status))
    self.bfxapi._emit('order_closed', order, trade)
    await self._confirm_order(order, trade)

  async def confirm_order_update(self, raw_ws_data):
    # order created but partially filled
    # [0, 'ou', [1151351581, None, 1542629457873, 'tBTCUSD', 1542629458071, 
    # 1542629458189, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE', 
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX', 
    # None, None, None]]
    order = Order(raw_ws_data[2])
    trade = Trade(order)
    self.logger.info("Order update: {} {}".format(order, trade))
    self.bfxapi._emit('order_update', order, trade)
    await self._confirm_order(order, trade)

  async def confirm_order_new(self, raw_ws_data):
    # order created but not executed /  created but partially filled
    # [0, 'on', [1151351563, None, 1542624024383, 'tBTCUSD', 1542624024596,
    # 1542624024617, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE',
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX',
    # None, None, None]]
    order = Order(raw_ws_data[2])
    trade = Trade(order)
    self.logger.info("Order new: {} {}".format(order, trade))
    self.bfxapi._emit('order_new', order, trade)
    await self._confirm_order(order, trade)

  def _gen_unqiue_cid(self):
    return int(round(time.time() * 1000))

  async def submit_order(self, symbol, price, amount, market_type,
      hidden=False, onComplete=None, onError=None, *args, **kwargs):
    order_id = self._gen_unqiue_cid()
    # send order over websocket
    payload = {
      "cid": order_id,
      "type": str(market_type),
      "symbol": symbol,
      "amount": str(amount),
      "price": str(price)
    }
    self.pending_orders[order_id] = (onComplete, onError)
    await self.bfxapi._send_auth_command('on', payload)
    self.logger.info("Order cid={} ({} {} @ {}) dispatched".format(
      order_id, symbol, amount, price))

  async def update_order(self, orderId, price=None, amount=None, delta=None,
    price_aux_limit=None, price_trailing=None, flags=None, time_in_force=None,
    onComplete=None, onError=None):
    payload = { "id": orderId }
    if price is not None:
      payload['price'] = str(price)
    if amount is not None:
      payload['amount'] = str(amount)
    if delta is not None:
      payload['delta'] = str(delta)
    if price_aux_limit is not None:
      payload['price_aux_limit'] = str(price_aux_limit)
    if price_trailing is not None:
      payload['price_trailing'] = str(price_trailing)
    if flags is not None:
      payload['flags'] = str(flags)
    if time_in_force is not None:
      payload['time_in_force'] = str(time_in_force)
    self.pending_orders[orderId] = (onComplete, onError)
    await self.bfxapi._send_auth_command('ou', payload)
    self.logger.info("Update Order order_id={} dispatched".format(orderId))

  async def cancel_order(self, orderId, onComplete=None, onError=None):
    self.pending_orders[orderId] = (onComplete, onError)
    await self.bfxapi._send_auth_command('oc', { 'id': orderId })
    self.logger.info("Order cancel order_id={} dispatched".format(orderId))

  async def cancel_order_multi(self, orderIds, onComplete=None, onError=None):
    self.pending_orders[orderIds[0]] = (onComplete, onError)
    await self.bfxapi._send_auth_command('oc', { 'id': orderIds })
    self.logger.info("Order cancel order_ids={} dispatched".format(orderIds))
