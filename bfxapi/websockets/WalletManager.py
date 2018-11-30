
from ..models import Wallet

class WalletManager:

  def __init__(self):
    self.wallets = {}

  def _update_from_snapshot(self, raw_ws_data):
    # [0, 'ws', [['exchange', 'BTC', 41.25809589, 0, None], ['exchange', 'USD', 62761.86070104, 0, None]]]
    wData = raw_ws_data[2]
    self.wallets = {}
    for wallet in wData:
      new_wallet = Wallet(wallet[0], wallet[1], wallet[2], wallet[3])
      self.wallets[new_wallet.key] = new_wallet
    return self.get_wallets()

  def _update_from_event(self, raw_ws_data):
    # [0,"wu",["exchange","USD",62761.86070104,0,61618.66070104]]
    wallet = raw_ws_data[2]
    new_wallet = Wallet(wallet[0], wallet[1], wallet[2], wallet[3])
    self.wallets[new_wallet.key] = new_wallet
    return new_wallet

  def get_wallets(self):
    return list(self.wallets.values())

