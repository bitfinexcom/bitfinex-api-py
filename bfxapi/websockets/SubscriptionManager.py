import json
import asyncio
import time

from ..utils.CustomLogger import CustomLogger
from ..models import Subscription

class SubscriptionManager:

  def __init__(self, bfxapi, logLevel='INFO'):
    self.pending_subscriptions = {}
    self.subscriptions_chanid = {}
    self.subscriptions_subid = {}
    self.unsubscribe_callbacks = {}
    self.bfxapi = bfxapi
    self.logger = CustomLogger('BfxSubscriptionManager', logLevel=logLevel)

  async def subscribe(self, channel_name, symbol, timeframe=None, **kwargs):
    """
    Subscribe to a new channel

    @param channel_name: the name of the channel i.e 'books', 'candles'
    @param symbol: the trading symbol i.e 'tBTCUSD'
    @param timeframe: sepecifies the data timeframe between each candle (only required
      for the candles channel)
    """
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
    """
    Unsubscribe from the channel with the given chanId

    @param onComplete: function called when the bitfinex websocket resoponds with
      a signal that confirms the subscription has been unsubscribed to
    """
    sub = self.subscriptions_chanid[chanId]
    if onComplete:
      self.unsubscribe_callbacks[sub.sub_id] = onComplete
    if sub.is_subscribed():
      await self.subscriptions_chanid[chanId].unsubscribe()

  async def resubscribe(self, chanId):
    """
    Unsubscribes and then subscribes to the channel with the given Id

    This function is mostly used to force the channel to produce a fresh snapshot.
    """
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
    """
    Returns True if the channel with the given chanId is currenly subscribed to
    """
    if chanId not in self.subscriptions_chanid:
      return False
    return self.subscriptions_chanid[chanId].is_subscribed()

  async def unsubscribe_all(self):
    """
    Unsubscribe from all channels.
    """
    task_batch = []
    for chanId in self.subscriptions_chanid:
      sub = self.get(chanId)
      if sub.is_subscribed():
        task_batch += [
          asyncio.ensure_future(self.unsubscribe(chanId))
        ]
    await asyncio.wait(*[ task_batch ])

  async def resubscribe_all(self):
    """
    Unsubscribe and then subscribe to all channels
    """
    task_batch = []
    for chanId in self.subscriptions_chanid:
      task_batch += [
        asyncio.ensure_future(self.resubscribe(chanId))
      ]
    await asyncio.wait(*[ task_batch ])
