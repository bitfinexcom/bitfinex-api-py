
class Wallet:

  def __init__(self, wType, currency, balance, unsettled_interest):
    self.type = wType
    self.currency = currency
    self.balance = balance
    self.unsettled_interest = unsettled_interest
    self.key = "{}_{}".format(wType, currency)

  def set_balance(self, data):
    self.balance = data

  def set_unsettled_interest(self, data):
    self.unsettled_interest = data

  def __str__(self):
    return "Wallet <'{}_{}' balance='{}' unsettled='{}'>".format(
      self.type, self.currency, self.balance, self.unsettled_interest)
