# python -c "import examples.rest.public.conf"

from bfxapi import Client

bfx = Client()

# Prints a map from symbols to their API symbols
print(bfx.rest.public.conf("pub:map:currency:sym"))

# Prints all the available exchange trading pairs
print(bfx.rest.public.conf("pub:list:pair:exchange"))

# Prints all the available funding currencies
print(bfx.rest.public.conf("pub:list:currency"))
