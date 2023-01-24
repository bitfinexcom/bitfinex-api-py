# python -c "from examples.rest.get_pulse_data import *"

import time

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST
)

now = int(round(time.time() * 1000))

messages = bfx.rest.public.get_pulse_history(end=now, limit=100)

for message in messages:
    print(f"Message: {message}")
    print(message.CONTENT)
    print(message.PROFILE.PICTURE)

profile = bfx.rest.public.get_pulse_profile("News")
print(f"Profile: {profile}")
print(f"Profile picture: {profile.PICTURE}")