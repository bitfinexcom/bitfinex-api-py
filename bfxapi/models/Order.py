import time
import datetime

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
  def __init__(self, id, gId, cId, symbol, mtsCreate, mtsUpdate, amount, amountOrig, oType,
      typePrev, flags, status, price, priceAvg, priceTrailing, priceAuxLimit, notfiy, placeId):
    self.id =  id
    self.gId = gId
    self.cId = cId
    self.symbol = symbol
    self.mtsCreate = mtsCreate
    self.mtsUpdate = mtsUpdate
    self.amount = amount
    self.amountOrig = amountOrig
    self.type = oType
    self.typePrev = typePrev
    self.flags = flags
    self.status = status
    self.price = price
    self.priceAvg = priceAvg
    self.priceTrailing = priceTrailing
    self.priceAuxLimit = priceAuxLimit
    self.notfiy = notfiy
    self.placeId = placeId

    self.is_pending_bool = True
    self.is_confirmed_bool = False
    self.is_open_bool = False

    self.date = datetime.datetime.fromtimestamp(mtsCreate/1000.0)
    if priceAvg:
      ## if cancelled then priceAvg wont exist
      self.fee = (priceAvg * abs(amount)) * 0.002

  @staticmethod
  def from_raw_order(raw_order):
    id =  raw_order[OrderClosedModel.ID]
    gId = raw_order[OrderClosedModel.GID]
    cId = raw_order[OrderClosedModel.CID]
    symbol = raw_order[OrderClosedModel.SYMBOL]
    mtsCreate = raw_order[OrderClosedModel.MTS_CREATE]
    mtsUpdate = raw_order[OrderClosedModel.MTS_UPDATE]
    amount = raw_order[OrderClosedModel.AMOUNT]
    amountOrig = raw_order[OrderClosedModel.AMOUNT_ORIG]
    oType = raw_order[OrderClosedModel.TYPE]
    typePrev = raw_order[OrderClosedModel.TYPE_PREV]
    flags = raw_order[OrderClosedModel.FLAGS]
    status = raw_order[OrderClosedModel.STATUS]
    price = raw_order[OrderClosedModel.PRICE]
    priceAvg = raw_order[OrderClosedModel.PRIVE_AVG]
    priceTrailing = raw_order[OrderClosedModel.PRICE_TRAILING]
    priceAuxLimit = raw_order[OrderClosedModel.PRICE_AUX_LIMIT]
    notfiy = raw_order[OrderClosedModel.NOTIFY]
    placeId = raw_order[OrderClosedModel.PLACE_ID]

    return Order(id, gId, cId, symbol, mtsCreate, mtsUpdate, amount, amountOrig, oType,
      typePrev, flags, status, price, priceAvg, priceTrailing, priceAuxLimit, notfiy, placeId)

  def set_confirmed(self):
    self.is_pending_bool = False
    self.is_confirmed_bool = True

  def set_open_state(self, isOpen):
    self.is_open_bool = isOpen

  def isOpen(self):
    return self.is_open_bool

  def isPending(self):
    return self.is_pending_bool

  def isConfirmed(self):
    return self.is_confirmed_bool
  
  def __str__(self):
    ''' Allow us to print the Order object in a pretty format '''
    return "Order <'{0}' mtsCreate={1} {2}>".format(self.symbol, self.mtsCreate,
      self.status)
