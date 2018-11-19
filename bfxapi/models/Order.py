import time

class OrderClosedModel:
  ID = 0
  GID = 1
  CID = 2
  SYMBOL = 3
  MTS_CREATE = 4
  MTS_UPDATE = 5
  AMOUNT = 6
  AMOUNT_ORIG = 7
  TYPE = 8
  TYPE_PREV = 9
  FLAGS = 12
  STATUS = 13
  PRICE = 16
  PRIVE_AVG = 17
  PRICE_TRAILING = 18
  PRICE_AUX_LIMIT = 19
  NOTIFY = 23
  PLACE_ID = 25

def now_in_mills():
  return int(round(time.time() * 1000))

class Order:
  def __init__(self, closingOrderArray):
    self.id =  closingOrderArray[OrderClosedModel.ID]
    self.gId = closingOrderArray[OrderClosedModel.GID]
    self.cId = closingOrderArray[OrderClosedModel.CID]
    self.symbol = closingOrderArray[OrderClosedModel.SYMBOL]
    self.mtsCreate = closingOrderArray[OrderClosedModel.MTS_CREATE]
    self.mtsUpdate = closingOrderArray[OrderClosedModel.MTS_UPDATE]
    self.amount = closingOrderArray[OrderClosedModel.AMOUNT]
    self.amountOrig = closingOrderArray[OrderClosedModel.AMOUNT_ORIG]
    self.type = closingOrderArray[OrderClosedModel.TYPE]
    self.typePrev = closingOrderArray[OrderClosedModel.TYPE_PREV]
    self.flags = closingOrderArray[OrderClosedModel.FLAGS]
    self.status = closingOrderArray[OrderClosedModel.STATUS]
    self.price = closingOrderArray[OrderClosedModel.PRICE]
    self.priceAvg = closingOrderArray[OrderClosedModel.PRIVE_AVG]
    self.priceTrailing = closingOrderArray[OrderClosedModel.PRICE_TRAILING]
    self.priceAuxLimit = closingOrderArray[OrderClosedModel.PRICE_AUX_LIMIT]
    self.notfiy = closingOrderArray[OrderClosedModel.NOTIFY]
    self.placeId = closingOrderArray[OrderClosedModel.PLACE_ID]

  
  def __str__(self):
    ''' Allow us to print the Order object in a pretty format '''
    return "Order <'{0}' mtsCreate={1} {2}>".format(self.symbol, self.mtsCreate,
      self.status)
