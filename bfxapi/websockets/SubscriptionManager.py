import json
import asyncio
import time

from ..utils.CustomLogger import CustomLogger

class Subscription:

  def __init__(self, ws, channel_name, symbol, timeframe=None, **kwargs):
    self.ws = ws
    self.channel_name = channel_name
    self.symbol = symbol
    self.timeframe = timeframe
    self.is_subscribed_bool = False
    self.key = None
    if timeframe:
      self.key = 'trade:{}:{}'.format(self.timeframe, self.symbol)
    self.sub_id = int(round(time.time() * 1000))
    self.send_payload = self._generate_payload(**kwargs)

  async def subscribe(self):
    await self.ws.send(json.dumps(self.get_send_payload()))

  async def unsubscribe(self):
    if not self.is_subscribed():
      raise Exception("Subscription is not subscribed to websocket")
    payload = { 'event': 'unsubscribe', 'chanId': self.chanId }
    await self.ws.send(json.dumps(payload))

  def confirm_subscription(self, chanId):
    self.is_subscribed_bool = True
    self.chanId = chanId

  def confirm_unsubscribe(self):
    self.is_subscribed_bool = False

  def is_subscribed(self):
    return self.is_subscribed_bool

  def _generate_payload(self, **kwargs):
    payload = { 'event': 'subscribe', 'channel': self.channel_name, 'symbol': self.symbol }
    if self.timeframe:
      payload['key'] = self.key
    payload.update(**kwargs)
    return payload

  def get_send_payload(self):
    return self.send_payload

class SubscriptionManager:

  def __init__(self, bfxapi, logLevel='INFO'):
    self.pending_subscriptions = {}
    self.subscriptions_chanid = {}
    self.subscriptions_subid = {}
    self.unsubscribe_callbacks = {}
    self.bfxapi = bfxapi
    self.logger = CustomLogger('BfxSubscriptionManager', logLevel=logLevel)

  async def subscribe(self, channel_name, symbol, timeframe=None, **kwargs):
    # create a new subscription
    subscription = Subscription(self.bfxapi.ws, channel_name, symbol, timeframe, **kwargs)
    self.logger.info("Subscribing to channel {}".format(channel_name))
    key = "{}_{}".format(channel_name, subscription.key or symbol)
    self.pending_subscriptions[key] = subscription
    await subscription.subscribe()

  async def confirm_subscription(self, raw_ws_data):
    # {"event":"subscribed","channel":"trades","chanId":1,"symbol":"tBTCUSD","pair":"BTCUSD"}
    # {"event":"subscribed","channel":"candles","chanId":351,"key":"trade:1m:tBTCUSD"}
    # {"event":"subscribed","channel":"book","chanId":4,"symbol":"tBTCUSD","prec":"P0","freq":"F0","len":"25","pair":"BTCUSD"}
    symbol = raw_ws_data.get("symbol", None)
    channel = raw_ws_data.get("channel")
    chanId = raw_ws_data.get("chanId")
    key = raw_ws_data.get("key", None)
    get_key = "{}_{}".format(channel, key or symbol)

    if chanId in self.subscriptions_chanid:
      # subscription has already existed in the past
      p_sub = self.subscriptions_chanid[chanId]
    else:
      # has just been created and is pending
      p_sub = self.pending_subscriptions[get_key]
      # remove from pending list
      del self.pending_subscriptions[get_key]
    p_sub.confirm_subscription(chanId)
    # add to confirmed list
    self.subscriptions_chanid[chanId] = p_sub
    self.subscriptions_subid[p_sub.sub_id] = p_sub
    self.bfxapi._emit('subscribed', p_sub)

  async def confirm_unsubscribe(self, raw_ws_data):
    chanId = raw_ws_data.get("chanId")
    sub = self.subscriptions_chanid[chanId]
    sub.confirm_unsubscribe()
    self.bfxapi._emit('unsubscribed', sub)
    # call onComplete callback if exists
    if sub.sub_id in self.unsubscribe_callbacks:
      await self.unsubscribe_callbacks[sub.sub_id]()
      del self.unsubscribe_callbacks[sub.sub_id]

  def get(self, chanId):
    return self.subscriptions_chanid[chanId]

  async def unsubscribe(self, chanId, onComplete=None):
    sub = self.subscriptions_chanid[chanId]
    if onComplete:
      self.unsubscribe_callbacks[sub.sub_id] = onComplete
    if sub.is_subscribed():
      await self.subscriptions_chanid[chanId].unsubscribe()

  async def resubscribe(self, chanId):
    sub = self.subscriptions_chanid[chanId]
    async def re_sub():
      await sub.subscribe()
    if sub.is_subscribed():
      # unsubscribe first and call callback to subscribe
      await self.unsubscribe(chanId, re_sub)
    else:
      # already unsibscribed, so just subscribe
      await sub.subscribe()

  def is_subscribed(self, chanId):
    if chanId not in self.subscriptions_chanid:
      return False
    return self.subscriptions_chanid[chanId].is_subscribed()

  async def unsubscribe_all(self):
    task_batch = []
    for chanId in self.subscriptions_chanid:
      sub = self.get(chanId)
      if sub.is_subscribed():
        task_batch += [
          asyncio.ensure_future(self.unsubscribe(chanId))
        ]
    await asyncio.wait(*[ task_batch ])

  async def resubscribe_all(self):
    task_batch = []
    for chanId in self.subscriptions_chanid:
      task_batch += [
        asyncio.ensure_future(self.resubscribe(chanId))
      ]
    await asyncio.wait(*[ task_batch ])
