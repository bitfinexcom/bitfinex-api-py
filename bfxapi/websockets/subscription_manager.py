"""
Module used to house all of the functions/classes used to handle
subscriptions
"""

import json
import asyncio
import time

from ..utils.custom_logger import CustomLogger
from ..models import Subscription

MAX_CHANNEL_COUNT = 25

class SubscriptionManager:

    def __init__(self, bfxapi, logLevel='INFO'):
        self.pending_subscriptions = {}
        self.subscriptions_chanid = {}
        self.subscriptions_subid = {}
        self.unsubscribe_callbacks = {}
        self.bfxapi = bfxapi
        self.logger = CustomLogger('BfxSubscriptionManager', logLevel=logLevel)

    def get_sub_count_by_socket(self, socket_id):
        count = 0
        for sub in self.subscriptions_chanid.values():
            if sub.socket.id == socket_id and sub.is_subscribed():
                count += 1
        for sub in self.pending_subscriptions.values():
            if sub.socket.id == socket_id:
                count += 1
        return count

    async def subscribe(self, channel_name, symbol, key=None, timeframe=None, **kwargs):
        """
        Subscribe to a new channel

        @param channel_name: the name of the channel i.e 'books', 'candles'
        @param symbol: the trading symbol i.e 'tBTCUSD'
        @param timeframe: sepecifies the data timeframe between each candle (only required
          for the candles channel)
        """
        if self.bfxapi.get_total_available_capcity() < 2:
            sId = self.bfxapi._start_new_socket()
            self.bfxapi._wait_for_socket(sId)
            soc = self.bfxapi.sockets[sId]
            socket = self.bfxapi.sockets[sId]
        else:
            # get the socket with the least amount of subscriptions
            socket = self.bfxapi.get_most_available_socket()
        # create a new subscription
        subscription = Subscription(
            socket, channel_name, symbol, key, timeframe, **kwargs)
        self.logger.info("Subscribing to channel {}".format(channel_name))
        self.pending_subscriptions[subscription.get_key()] = subscription

        await subscription.subscribe()

    async def confirm_subscription(self, socket_id, raw_ws_data):
        symbol = raw_ws_data.get("symbol", None)
        channel = raw_ws_data.get("channel")
        chan_id = raw_ws_data.get("chanId")
        key = raw_ws_data.get("key", None)
        get_key = "{}_{}".format(channel, key or symbol)
        if chan_id in self.subscriptions_chanid:
            # subscription has already existed in the past
            p_sub = self.subscriptions_chanid[chan_id]
        elif get_key in self.pending_subscriptions:
            # has just been created and is pending
            p_sub = self.pending_subscriptions[get_key]
            # remove from pending list
            del self.pending_subscriptions[get_key]
        else:
            # might have been disconnected, so we need to check if exists
            # as subscribed but with a new channel ID
            for sub in self.subscriptions_chanid.values():
                if sub.get_key() == get_key and not sub.is_subscribed():
                    # delete old channelId
                    del self.subscriptions_chanid[sub.chan_id]
                    p_sub = sub
                    break
        if p_sub is None:
            # no sub matches confirmation
            self.logger.warn("unknown subscription confirmed {}".format(get_key))
            return

        p_sub.confirm_subscription(chan_id)
        # add to confirmed list
        self.subscriptions_chanid[chan_id] = p_sub
        self.subscriptions_subid[p_sub.sub_id] = p_sub
        self.bfxapi._emit('subscribed', p_sub)

    async def confirm_unsubscribe(self, socket_id, raw_ws_data):
        chan_id = raw_ws_data.get("chanId")
        sub = self.subscriptions_chanid[chan_id]
        sub.confirm_unsubscribe()
        # call onComplete callback if exists
        if sub.sub_id in self.unsubscribe_callbacks:
            await self.unsubscribe_callbacks[sub.sub_id]()
            del self.unsubscribe_callbacks[sub.sub_id]
        self.bfxapi._emit('unsubscribed', sub)

    def get(self, chan_id):
        return self.subscriptions_chanid[chan_id]

    def set_unsubscribed_by_socket(self, socket_id):
        """
        Sets all f the subscriptions ot state 'unsubscribed'
        """
        for sub in self.subscriptions_chanid.values():
            if sub.socket.id == socket_id:
                sub.confirm_unsubscribe()

    def set_all_unsubscribed(self):
        """
        Sets all f the subscriptions ot state 'unsubscribed'
        """
        for sub in self.subscriptions_chanid.values():
            sub.confirm_unsubscribe()

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
            # already unsubscribed, so just subscribe
            await sub.subscribe()

    def channel_count(self):
        """
        Returns the number of cannels
        """
        return len(self.pending_subscriptions) + len(self.subscriptions_chanid)

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
        if len(task_batch) == 0:
            return
        await asyncio.wait(*[task_batch])

    async def resubscribe_by_socket(self, socket_id):
        """
        Unsubscribe channels on socket and then subscribe to all channels
        """
        task_batch = []
        for sub in self.subscriptions_chanid.values():
            if sub.socket.id == socket_id:
                task_batch += [
                    asyncio.ensure_future(self.resubscribe(sub.chan_id))
                ]
        if len(task_batch) == 0:
            return
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
        if len(task_batch) == 0:
            return
        await asyncio.wait(*[task_batch])
