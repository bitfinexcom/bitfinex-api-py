# python -c "import examples.rest.get_pulse_data"

import time

from bfxapi.client import Client, REST_HOST

bfx = Client(
    REST_HOST=REST_HOST
)

now = int(round(time.time() * 1000))

messages = bfx.rest.public.get_pulse_history(end=now, limit=100)

for message in messages:
    print(f"Message: {message}")
    print(message.content)
    print(message.profile.picture)

profile = bfx.rest.public.get_pulse_profile("News")
print(f"Profile: {profile}")
print(f"Profile picture: {profile.picture}")