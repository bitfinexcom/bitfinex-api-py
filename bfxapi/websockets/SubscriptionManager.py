"""
Module used to house all of the functions/classes used to handle
subscriptions
"""

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
        subscription = Subscription(
            self.bfxapi.ws, channel_name, symbol, timeframe, **kwargs)
        self.logger.info("Subscribing to channel {}".format(channel_name))
        key = "{}_{}".format(channel_name, subscription.key or symbol)
        self.pending_subscriptions[key] = subscription
        await subscription.subscribe()

    async def confirm_subscription(self, raw_ws_data):
        symbol = raw_ws_data.get("symbol", None)
        channel = raw_ws_data.get("channel")
        chan_id = raw_ws_data.get("chanId")
        key = raw_ws_data.get("key", None)
        get_key = "{}_{}".format(channel, key or symbol)

        if chan_id in self.subscriptions_chanid:
            # subscription has already existed in the past
            p_sub = self.subscriptions_chanid[chan_id]
        else:
            # has just been created and is pending
            p_sub = self.pending_subscriptions[get_key]
            # remove from pending list
            del self.pending_subscriptions[get_key]
        p_sub.confirm_subscription(chan_id)
        # add to confirmed list
        self.subscriptions_chanid[chan_id] = p_sub
        self.subscriptions_subid[p_sub.sub_id] = p_sub
        self.bfxapi._emit('subscribed', p_sub)

    async def confirm_unsubscribe(self, raw_ws_data):
        chan_id = raw_ws_data.get("chanId")
        sub = self.subscriptions_chanid[chan_id]
        sub.confirm_unsubscribe()
        self.bfxapi._emit('unsubscribed', sub)
        # call onComplete callback if exists
        if sub.sub_id in self.unsubscribe_callbacks:
            await self.unsubscribe_callbacks[sub.sub_id]()
            del self.unsubscribe_callbacks[sub.sub_id]

    def get(self, chan_id):
        return self.subscriptions_chanid[chan_id]

    async def unsubscribe(self, chan_id, onComplete=None):
        """
        Unsubscribe from the channel with the given chanId

        @param onComplete: function called when the bitfinex websocket resoponds with
          a signal that confirms the subscription has been unsubscribed to
        """
        sub = self.subscriptions_chanid[chan_id]
        if onComplete:
            self.unsubscribe_callbacks[sub.sub_id] = onComplete
        if sub.is_subscribed():
            await self.subscriptions_chanid[chan_id].unsubscribe()

    async def resubscribe(self, chan_id):
        """
        Unsubscribes and then subscribes to the channel with the given Id

        This function is mostly used to force the channel to produce a fresh snapshot.
        """
        sub = self.subscriptions_chanid[chan_id]

        async def re_sub():
            await sub.subscribe()
        if sub.is_subscribed():
            # unsubscribe first and call callback to subscribe
            await self.unsubscribe(chan_id, re_sub)
        else:
            # already unsibscribed, so just subscribe
            await sub.subscribe()

    def is_subscribed(self, chan_id):
        """
        Returns True if the channel with the given chanId is currenly subscribed to
        """
        if chan_id not in self.subscriptions_chanid:
            return False
        return self.subscriptions_chanid[chan_id].is_subscribed()

    async def unsubscribe_all(self):
        """
        Unsubscribe from all channels.
        """
        task_batch = []
        for chan_id in self.subscriptions_chanid:
            sub = self.get(chan_id)
            if sub.is_subscribed():
                task_batch += [
                    asyncio.ensure_future(self.unsubscribe(chan_id))
                ]
        await asyncio.wait(*[task_batch])

    async def resubscribe_all(self):
        """
        Unsubscribe and then subscribe to all channels
        """
        task_batch = []
        for chan_id in self.subscriptions_chanid:
            task_batch += [
                asyncio.ensure_future(self.resubscribe(chan_id))
            ]
        await asyncio.wait(*[task_batch])
