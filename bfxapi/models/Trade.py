import datetime

class Trade:
  SHORT = 'SHORT'
  LONG = 'LONG'

  def __init__(self, order, tag=''):
    self.order = order
    self.amount = order.amount
    self.price = order.priceAvg
    self.fee = (order.priceAvg * abs(order.amount)) * 0.002
    self.mts = order.mtsCreate
    self.date = datetime.datetime.fromtimestamp(order.mtsCreate/1000.0)
    self.direction = self.SHORT if order.amount < 0 else self.LONG
    self.tag = tag
  
  def __str__(self):
    ''' Allow us to print the Trade object in a pretty format '''
    return "Trade {} @ {} fee={} <order='{}'>".format(
      self.amount, self.price, self.fee, self.order)
