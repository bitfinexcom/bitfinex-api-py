import json, asyncio, hmac, hashlib, time, websockets

from pyee.asyncio import AsyncIOEventEmitter

from .manager import Manager

from .errors import ConnectionNotOpen, AuthenticationCredentialsError

class BfxWebsocketClient(object):
    def __init__(self, host, API_KEY=None, API_SECRET=None):
        self.host, self.chanIds, self.event_emitter = host, dict(), AsyncIOEventEmitter()

        self.manager, self.websocket = Manager(event_emitter=self.event_emitter), None

        self.API_KEY, self.API_SECRET = API_KEY, API_SECRET

    def run_forever(self):
        asyncio.run(self.connect())

    async def connect(self):
        async for websocket in websockets.connect(self.host):
            self.websocket = websocket

            try:     
                self.event_emitter.emit("open")

                if self.API_KEY != None and self.API_SECRET != None:
                    self.authenticate(self.API_KEY, self.API_SECRET)

                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "subscribed":
                        del message["event"]
                        self.chanIds[message["chanId"]] = message
                        self.event_emitter.emit("subscribed", message)

                    elif isinstance(message, dict) and message["event"] == "unsubscribed":
                        if message["status"] == "OK":
                            del self.chanIds[message["chanId"]]

                    elif isinstance(message, dict) and message["event"] == "auth":
                        if message["status"] == "OK":
                            self.chanIds[message["chanId"]] = message

                            self.event_emitter.emit("authenticated", message)
                        else: raise AuthenticationCredentialsError("Cannot authenticate with given API-KEY and API-SECRET.")

                    elif isinstance(message, list):
                        chanId, parameters = message[0], message[1:]
                        
                        self.manager.handle(self.chanIds[chanId], *parameters)
            except websockets.ConnectionClosed:
                continue
        
    @staticmethod
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