"""
Module used to describe all of the different data types
"""

import time
import json


class Subscription:
    """
    Object used to represent an individual subscription to the websocket.
    This class also exposes certain functions which helps to manage the subscription
    such as unsibscribe and subscribe.
    """

    def __init__(self, ws, channel_name, symbol, timeframe=None, **kwargs):
        self._ws = ws
        self.channel_name = channel_name
        self.symbol = symbol
        self.timeframe = timeframe
        self.is_subscribed_bool = False
        self.key = None
        self.chan_id = None
        if timeframe:
            self.key = 'trade:{}:{}'.format(self.timeframe, self.symbol)
        self.sub_id = int(round(time.time() * 1000))
        self.send_payload = self._generate_payload(**kwargs)

    def confirm_subscription(self, chan_id):
        """
        Update the subscription to confirmed state
        """
        self.is_subscribed_bool = True
        self.chan_id = chan_id

    async def unsubscribe(self):
        """
        Send an unsubscription request to the bitfinex socket
        """
        if not self.is_subscribed():
            raise Exception("Subscription is not subscribed to websocket")
        payload = {'event': 'unsubscribe', 'chan_id': self.chan_id}
        await self._ws.send(json.dumps(payload))

    async def subscribe(self):
        """
        Send a subscription request to the bitfinex socket
        """
        await self._ws.send(json.dumps(self._get_send_payload()))

    def confirm_unsubscribe(self):
        """
        Update the subscription to unsubscribed state
        """
        self.is_subscribed_bool = False

    def is_subscribed(self):
        """
        Check if the subscription is currently subscribed

        @return bool: True if subscribed else False
        """
        return self.is_subscribed_bool

    def _generate_payload(self, **kwargs):
        payload = {'event': 'subscribe',
                   'channel': self.channel_name, 'symbol': self.symbol}
        if self.timeframe:
            payload['key'] = self.key
        payload.update(**kwargs)
        return payload

    def _get_send_payload(self):
        return self.send_payload
