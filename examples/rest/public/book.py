# python -c "import examples.rest.public.book"

from typing import List

from bfxapi import Client
from bfxapi.types import (
    FundingCurrencyBook,
    FundingCurrencyRawBook,
    TradingPairBook,
    TradingPairRawBook,
)

bfx = Client()

t_book: List[TradingPairBook] = bfx.rest.public.get_t_book(
    "tBTCUSD", precision="P0", len=25
)

print("25 price points of tBTCUSD order book (with precision P0):", t_book)

t_raw_book: List[TradingPairRawBook] = bfx.rest.public.get_t_raw_book("tBTCUSD")

print("tBTCUSD raw order book:", t_raw_book)

f_book: List[FundingCurrencyBook] = bfx.rest.public.get_f_book(
    "fUSD", precision="P0", len=25
)

print("25 price points of fUSD order book (with precision P0):", f_book)

f_raw_book: List[FundingCurrencyRawBook] = bfx.rest.public.get_f_raw_book("fUSD")

print("fUSD raw order book:", f_raw_book)
