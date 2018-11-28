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
  def __init__(self, bfxapi, closingOrderArray):
    self.bfxapi = bfxapi
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
    self.is_pending_bool = True
    self.is_confirmed_bool = False
    self.is_open_bool = False

  async def update(self, price=None, amount=None, delta=None, price_aux_limit=None,
      price_trailing=None, flags=None, time_in_force=None):
    payload = { "id": self.id }
    if price is not None:
      payload['price'] = str(price)
    if amount is not None:
      payload['amount'] = str(amount)
    if delta is not None:
      payload['delta'] = str(delta)
    if price_aux_limit is not None:
      payload['price_aux_limit'] = str(price_aux_limit)
    if price_trailing is not None:
      payload['price_trailing'] = str(price_trailing)
    if flags is not None:
      payload['flags'] = str(flags)
    if time_in_force is not None:
      payload['time_in_force'] = str(time_in_force)
    await self.bfxapi._send_auth_command('ou', payload)

  async def close(self):
    await self.bfxapi._send_auth_command('oc', { 'id': self.id })

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
