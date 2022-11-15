import json, asyncio, hmac, hashlib, time, websockets

from pyee.asyncio import AsyncIOEventEmitter

from .handlers import Channels, PublicChannelsHandler, AuthenticatedChannelsHandler

from .errors import BfxWebsocketException, ConnectionNotOpen, InvalidAuthenticationCredentials, OutdatedClientVersion

HEARTBEAT = "hb"

class BfxWebsocketClient(object):
    VERSION = 1

    def __init__(self, host, API_KEY=None, API_SECRET=None):
        self.host, self.chanIds, self.event_emitter = host, dict(), AsyncIOEventEmitter()

        self.websocket, self.API_KEY, self.API_SECRET = None, API_KEY, API_SECRET

        self.handlers = {
            "public": PublicChannelsHandler(event_emitter=self.event_emitter),
            "authenticated": AuthenticatedChannelsHandler(event_emitter=self.event_emitter)
        }

    async def connect(self):
        async for websocket in websockets.connect(self.host):
            self.websocket = websocket

            try:     
                self.event_emitter.emit("open")

                if self.API_KEY != None and self.API_SECRET != None:
                    await self.authenticate(self.API_KEY, self.API_SECRET)

                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "info" and "version" in message:
                        if BfxWebsocketClient.VERSION != message["version"]:
                            raise OutdatedClientVersion(f"Mismatch between the client version and the server version. Update the library to the latest version to continue (client version: {BfxWebsocketClient.VERSION}, server version: {message['version']}).")
                    elif isinstance(message, dict) and message["event"] == "subscribed":
                        self.chanIds[message["chanId"]] = message

                        self.event_emitter.emit("subscribed", message)
                    elif isinstance(message, dict) and message["event"] == "unsubscribed":
                        if message["status"] == "OK":
                            del self.chanIds[message["chanId"]]
                    elif isinstance(message, dict) and message["event"] == "auth":
                        if message["status"] == "OK":
                            self.event_emitter.emit("authenticated", message)
                        else: raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")
                    elif isinstance(message, dict) and message["event"] == "error":
                        self.event_emitter.emit("error", message["code"], message["msg"])
                    elif isinstance(message, list) and ((chanId := message[0]) or True) and message[1] != HEARTBEAT:
                        if chanId == 0:
                            self.handlers["authenticated"].handle(message[1], message[2])
                        else: self.handlers["public"].handle(self.chanIds[chanId], *message[1:])
            except websockets.ConnectionClosed:
                continue

    def __require_websocket_connection(function):
        async def wrapper(self, *args, **kwargs):
            if self.websocket == None or self.websocket.open == False:
                raise ConnectionNotOpen("No open connection with the server.")
        
            await function(self, *args, **kwargs)

        return wrapper

    @__require_websocket_connection
    async def subscribe(self, channel, **kwargs):
        await self.websocket.send(json.dumps({
            "event": "subscribe",
            "channel": channel,
            **kwargs
        }))

    @__require_websocket_connection
    async def unsubscribe(self, chanId):
        await self.websocket.send(json.dumps({
            "event": "unsubscribe",
            "chanId": chanId
        }))

    @__require_websocket_connection
    async def authenticate(self, API_KEY, API_SECRET, filter=None):
        data = { "event": "auth", "filter": filter, "apiKey": API_KEY }

        data["authNonce"] = int(time.time()) * 1000

        data["authPayload"] = "AUTH" + str(data["authNonce"])

        data["authSig"] = hmac.new(
            API_SECRET.encode("utf8"),
            data["authPayload"].encode("utf8"),
            hashlib.sha384 
        ).hexdigest()

        await self.websocket.send(json.dumps(data))

    async def clear(self):
        for chanId in self.chanIds.keys():
            await self.unsubscribe(chanId)

    def on(self, event):
        def handler(function):
            self.event_emitter.on(event, function)

        return handler 

    def once(self, event):
        def handler(function):
            self.event_emitter.once(event, function)

        return handler 

    def run(self): 
        asyncio.run(self.connect())