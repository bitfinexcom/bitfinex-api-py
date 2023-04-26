# python -c "import examples.rest.public.trades"

from typing import List

from bfxapi import Client, PUB_REST_HOST
from bfxapi.types import TradingPairTrade,  FundingCurrencyTrade
from bfxapi.rest.enums import Sort

bfx = Client(rest_host=PUB_REST_HOST)

t_trades: List[TradingPairTrade] = bfx.rest.public.get_t_trades("tBTCUSD", \
    limit=15, sort=Sort.ASCENDING)

print("Latest 15 trades for tBTCUSD (in ascending order):", t_trades)

f_trades: List[FundingCurrencyTrade] = bfx.rest.public.get_f_trades("fUSD", \
    limit=15, sort=Sort.DESCENDING)

print("Latest 15 trades for fUSD (in descending order):", f_trades)
