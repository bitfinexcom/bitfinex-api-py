import datetime

class Trade:
  SHORT = 'SHORT'
  LONG = 'LONG'

  def __init__(self, id, pair, mts_create, order_id, amount, price, order_type,
      order_price, maker, fee, fee_currency):
    self.id = id
    self.pair = pair
    self.mts_create = mts_create
    self.date = datetime.datetime.fromtimestamp(mts_create/1000.0)
    self.order_id = order_id
    self.amount = amount
    self.direction = Trade.SHORT if amount < 0 else Trade.LONG
    self.price = price
    self.order_type = order_type
    self.order_price = order_price
    self.maker = maker
    self.fee = fee
    self.fee_currency = fee_currency

  @staticmethod
  def from_raw_rest_trade(raw_trade):
    # [24224048, 'tBTCUSD', 1542800024000, 1151353484, 0.09399997, 19963, None, None, -1, -0.000188, 'BTC']
    return Trade(*raw_trade)
  
  def __str__(self):
    return "Trade '{}' x {} @ {} <direction='{}' fee={}>".format(
      self.pair, self.amount, self.price, self.direction, self.fee)
