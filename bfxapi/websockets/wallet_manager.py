"""
Module used to handle wallet updates and data types
"""

from ..models import Wallet


class WalletManager:
    """
    This class is used to interact with all of the different wallets
    """

    def __init__(self):
        self.wallets = {}

    def _update_from_snapshot(self, raw_ws_data):
        wData = raw_ws_data[2]
        self.wallets = {}
        for wallet in wData:
            new_wallet = Wallet(wallet[0], wallet[1], wallet[2], wallet[3], wallet[4])
            self.wallets[new_wallet.key] = new_wallet
        return self.get_wallets()

    def _update_from_event(self, raw_ws_data):
        wallet = raw_ws_data[2]
        new_wallet = Wallet(wallet[0], wallet[1], wallet[2], wallet[3], wallet[4])
        self.wallets[new_wallet.key] = new_wallet
        return new_wallet

    def get_wallets(self):
        return list(self.wallets.values())
