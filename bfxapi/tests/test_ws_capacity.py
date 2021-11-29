import pytest
import json
import time
import asyncio
from .helpers import (create_stubbed_client, ws_publish_connection_init, ws_publish_auth_accepted)

@pytest.mark.asyncio
async def test_ws_creates_new_socket():
  client = create_stubbed_client()
  client.ws.ws_capacity = 5
  # publish connection created message
  await ws_publish_connection_init(client.ws)
  # create a bunch of websocket subscriptions
  for symbol in ['tXRPBTC', 'tLTCUSD']:
    await client.ws.subscribe('candles', symbol, timeframe='1m')
    assert len(client.ws.sockets) == 1
  assert client.ws.get_total_available_capcity() == 3
  # subscribe to a few more to force the lib to create a new ws conenction
  for symbol in ['tETHBTC', 'tBTCUSD', 'tETHUSD', 'tLTCBTC']:
    await client.ws.subscribe('candles', symbol, timeframe='1m')
  assert len(client.ws.sockets) == 2
  assert client.ws.get_total_available_capcity() == 4

@pytest.mark.asyncio
async def test_ws_uses_authenticated_socket():
  client = create_stubbed_client()
  client.ws.ws_capacity = 2
  # publish connection created message
  await ws_publish_connection_init(client.ws)
  # create a bunch of websocket subscriptions
  for symbol in ['tXRPBTC', 'tLTCUSD', 'tETHBTC', 'tBTCUSD', 'tETHUSD', 'tLTCBTC']:
    await client.ws.subscribe('candles', symbol, timeframe='1m')
  # publish connection created message on socket (0 by default)
  await ws_publish_connection_init(client.ws)
  # send auth accepted (on socket by default)
  await ws_publish_auth_accepted(client.ws)
  # socket 0 should be the authenticated socket
  assert client.ws.get_authenticated_socket().id == 0
  # there should be no other authenticated sockets
  for socket in client.ws.sockets.values():
    if socket.id != 0:
      assert socket.isAuthenticated == False
