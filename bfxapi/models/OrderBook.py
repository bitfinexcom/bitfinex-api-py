import zlib

def preparePrice(price):
  # convert to 4 significant figures
  prepPrice = '{0:.4f}'.format(price)
  # remove decimal place if zero float
  return '{0:g}'.format(float(prepPrice))

class OrderBook:

  def __init__(self):
    self.asks = []
    self.bids = []

  def updateFromSnapshot(self, data):
    # [[4642.3, 1, 4.192], [4641.5, 1, 1]]
    for order in data:
      if len(order) is 4:
        if order[3] < 0:
          self.bids += [order]
        else:
          self.asks += [order]
      else:
        if order[2] < 0:
          self.asks += [order]
        else:
          self.bids += [order]

  def updateWith(self, order):
    if len(order) is 4:
      amount = order[3]
      count = order[2]
      side = self.bids if amount < 0 else self.asks
    else:
      amount = order[2]
      side = self.asks if amount < 0 else self.bids
      count = order[1]
    price = order[0]

    # if first item in ordebook
    if len(side) is 0:
      side += [order]
      return

    # match price level
    for index, sOrder in enumerate(side):
      sPrice = sOrder[0]
      if sPrice == price:
        if count is 0:
          del side[index]
          return
        else:
          # remove but add as new below
          del side[index]
    
    # if ob is initialised w/o all price levels
    if count is 0:
      return
    
    # add to book and sort lowest to highest
    side += [order]
    side.sort(key=lambda x: x[0], reverse=not amount < 0)
    return

  def checksum(self):
    data = []
    # take set of top 25 bids/asks
    for index in range(0, 25):
      if index < len(self.bids):
        bid = self.bids[index]
        price = bid[0]
        amount = bid[3] if len(bid) is 4 else bid[2]
        data += [preparePrice(price)]
        data += [str(amount)]
      if index < len(self.asks):
        ask = self.asks[index]
        price = ask[0]
        amount = ask[3] if len(ask) is 4 else ask[2]
        data += [preparePrice(price)]
        data += [str(amount)]
    checksumStr = ':'.join(data)
    # calculate checksum and force signed integer
    checksum = zlib.crc32(checksumStr.encode('utf8')) & 0xffffffff
    return checksum
