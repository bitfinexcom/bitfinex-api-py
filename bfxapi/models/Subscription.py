import time
import json

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
