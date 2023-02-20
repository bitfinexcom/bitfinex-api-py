# python -c "import examples.rest.public.conf"

from bfxapi import Client, PUB_REST_HOST

from bfxapi.rest.enums import Config

bfx = Client(REST_HOST=PUB_REST_HOST)

print("Available configs:", [ config.value for config in Config ])

# Prints a map from symbols to their API symbols (pub:map:currency:sym)
print (bfx.rest.public.conf(Config.MAP_CURRENCY_SYM))

# Prints all the available exchange trading pairs (pub:list:pair:exchange)
print(bfx.rest.public.conf(Config.LIST_PAIR_EXCHANGE))

# Prints all the available funding currencies (pub:list:currency)
print(bfx.rest.public.conf(Config.LIST_CURRENCY))