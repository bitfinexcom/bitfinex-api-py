# python -c "import examples.rest.public.trades"

from typing import List

from bfxapi import Client
from bfxapi.types import FundingCurrencyTrade, TradingPairTrade

bfx = Client()

t_trades: List[TradingPairTrade] = bfx.rest.public.get_t_trades(
    "tBTCUSD", limit=15, sort=+1
)

print("Latest 15 trades for tBTCUSD (in ascending order):", t_trades)

f_trades: List[FundingCurrencyTrade] = bfx.rest.public.get_f_trades(
    "fUSD", limit=15, sort=-1
)

print("Latest 15 trades for fUSD (in descending order):", f_trades)
