# python -c "import examples.rest.auth.get_wallets"

import os
from typing import List

from bfxapi import Client
from bfxapi.types import (
    DepositAddress,
    LightningNetworkInvoice,
    Notification,
    Transfer,
    Wallet,
    Withdrawal,
)

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

# Gets all user's available wallets
wallets: List[Wallet] = bfx.rest.auth.get_wallets()

# Transfers funds (0.001 ETH) from exchange wallet to funding wallet
A: Notification[Transfer] = bfx.rest.auth.transfer_between_wallets(
    from_wallet="exchange",
    to_wallet="funding",
    currency="ETH",
    currency_to="ETH",
    amount=0.001,
)

print("Transfer:", A.data)

# Retrieves the deposit address for bitcoin currency in exchange wallet.
B: Notification[DepositAddress] = bfx.rest.auth.get_deposit_address(
    wallet="exchange", method="bitcoin", op_renew=False
)

print("Deposit address:", B.data)

# Generates a lightning network deposit invoice
C: Notification[LightningNetworkInvoice] = bfx.rest.auth.generate_deposit_invoice(
    wallet="funding", currency="LNX", amount=0.001
)

print("Lightning network invoice:", C.data)

# Withdraws 1.0 UST from user's exchange wallet to address 0x742d35...
D: Notification[Withdrawal] = bfx.rest.auth.submit_wallet_withdrawal(
    wallet="exchange",
    method="tetheruse",
    address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    amount=1.0,
)

print("Withdrawal:", D.data)
