
class Position:

  def __init__(self, symbol, status, amount, bPrice, mFunding, mFundingType,
      profit_loss, profit_loss_perc, lPrice, lev):
      # [['tBTCUSD', 'ACTIVE', -2.37709587, 20720, -0.00066105, 0, 13115.99728968, 26.6296139, 104156.986252, -1.2332]]
    self.symbol = symbol
    self.status = status
    self.amount = amount
    self.base_price = bPrice
    self.margin_funding = mFunding
    self.margin_funding_type = mFundingType
    self.profit_loss = profit_loss
    self.profit_loss_percentage = profit_loss_perc
    self.liquidation_price = lPrice
    self.leverage = lev

  @staticmethod
  def from_raw_rest_position(raw_position):
    return Position(*raw_position)
  
  def __str__(self):
    ''' Allow us to print the Trade object in a pretty format '''
    return "Position '{}' {} x {} <Sstatus='{}' p&l={}>".format(
      self.symbol, self.base_price, self.amount, self.status, self.profit_loss)
