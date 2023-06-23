# python -c "import examples.rest.public.pulse_endpoints"

import datetime

from typing import List

from bfxapi import Client, PUB_REST_HOST

from bfxapi.types import PulseMessage, PulseProfile

bfx = Client(rest_host=PUB_REST_HOST)

# POSIX timestamp in milliseconds (check https://currentmillis.com/)
end = datetime.datetime(2020, 5, 2).timestamp() * 1000

# Retrieves 25 pulse messages up to 2020/05/02
messages: List[PulseMessage] = bfx.rest.public.get_pulse_message_history(end=end, limit=25)

for message in messages:
    print(f"Message author: {message.profile.nickname} ({message.profile.puid})")
    print(f"Title: <{message.title}>")
    print(f"Tags: {message.tags}\n")

profile: PulseProfile = bfx.rest.public.get_pulse_profile_details("News")
URL = profile.picture.replace("size", "small")
print(f"<{profile.nickname}>'s profile picture: https://s3-eu-west-1.amazonaws.com/bfx-pub/{URL}")
