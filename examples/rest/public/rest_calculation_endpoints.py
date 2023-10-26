# python -c "import examples.rest.public.rest_calculation_endpoints"

from bfxapi import Client
from bfxapi.types import FundingMarketAveragePrice, FxRate, TradingMarketAveragePrice

bfx = Client()

trading_market_average_price: TradingMarketAveragePrice = (
    bfx.rest.public.get_trading_market_average_price(
        symbol="tBTCUSD", amount=-100, price_limit=20000.5
    )
)

print("Average execution price for tBTCUSD:", trading_market_average_price.price_avg)

funding_market_average_price: FundingMarketAveragePrice = (
    bfx.rest.public.get_funding_market_average_price(
        symbol="fUSD", amount=100, period=2, rate_limit=0.00015
    )
)

print("Average execution rate for fUSD:", funding_market_average_price.rate_avg)

fx_rate: FxRate = bfx.rest.public.get_fx_rate(ccy1="USD", ccy2="EUR")

print("Exchange rate between USD and EUR:", fx_rate.current_rate)
