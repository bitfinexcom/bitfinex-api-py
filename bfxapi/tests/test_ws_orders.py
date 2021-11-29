import pytest
import json
import asyncio
from .helpers import (create_stubbed_client, ws_publish_auth_accepted, ws_publish_connection_init,
					  EventWatcher)

@pytest.mark.asyncio
async def test_submit_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	## send new order
	await client.ws.submit_order('tBTCUSD', 19000, 0.01, 'EXCHANGE MARKET')
	last_sent = client.ws.get_last_sent_item()
	sent_order_array = json.loads(last_sent['data'])
	assert sent_order_array[1] == "on"
	sent_order_json = sent_order_array[3]
	assert sent_order_json['type'] == "EXCHANGE MARKET"
	assert sent_order_json['symbol'] == "tBTCUSD"
	assert sent_order_json['amount'] == "0.01"
	assert sent_order_json['price'] == "19000"

@pytest.mark.asyncio
async def test_submit_update_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	## send new order
	await client.ws.update_order(123, price=100, amount=0.01, hidden=True)
	last_sent = client.ws.get_last_sent_item()
	sent_order_array = json.loads(last_sent['data'])
	assert sent_order_array[1] == "ou"
	sent_order_json = sent_order_array[3]
	# {"id": 123, "price": "100", "amount": "0.01", "flags": 64}
	assert sent_order_json['id'] == 123
	assert sent_order_json['price'] == "100"
	assert sent_order_json['amount'] == "0.01"
	assert sent_order_json['flags'] == 64

@pytest.mark.asyncio
async def test_submit_cancel_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	## send new order
	await client.ws.cancel_order(123)
	last_sent = client.ws.get_last_sent_item()
	sent_order_array = json.loads(last_sent['data'])
	assert sent_order_array[1] == "oc"
	sent_order_json = sent_order_array[3]
	assert sent_order_json['id'] == 123

@pytest.mark.asyncio
async def test_events_on_new_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)

	## look for new order confirmation
	o_new = EventWatcher.watch(client.ws, 'order_new')
	await client.ws.publish([0,"on",[1151718504,None,1548262833910,"tBTCUSD",1548262833379,1548262833410,-1,-1,"EXCHANGE LIMIT",None,None,None,0,"ACTIVE",None,None,15980,0,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	new_res = o_new.wait_until_complete()
	assert new_res.amount_orig == -1
	assert new_res.amount_filled == 0
	assert new_res.price == 15980
	assert new_res.type == 'EXCHANGE LIMIT'

	## look for order update confirmation
	o_update = EventWatcher.watch(client.ws, 'order_update')
	await client.ws.publish([0,"ou",[1151718504,None,1548262833910,"tBTCUSD",1548262833379,1548262846964,-0.5,-1,"EXCHANGE LIMIT",None,None,None,0,"PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	update_res = o_update.wait_until_complete()
	assert update_res.amount_orig == -1
	assert float(update_res.amount_filled) == -0.5
	assert update_res.price == 15980
	assert update_res.type == 'EXCHANGE LIMIT'

	## look for closed notification
	o_closed = EventWatcher.watch(client.ws, 'order_closed')
	await client.ws.publish([0,"oc",[1151718504,None,1548262833910,"tBTCUSD",1548262833379,1548262888016,0,-1,"EXCHANGE LIMIT",None,None,None,0,"EXECUTED @ 15980.0(-0.5): was PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	closed_res = o_closed.wait_until_complete()
	assert new_res.amount_orig == -1
	assert new_res.amount_filled == 0
	assert new_res.price == 15980
	assert new_res.type == 'EXCHANGE LIMIT'

@pytest.mark.asyncio
async def test_events_on_cancel_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)

	## Create new order
	await client.ws.publish([0,"on",[1151718565,None,1548325124885,"tBTCUSD",1548325123435,1548325123460,1,1,"EXCHANGE LIMIT",None,None,None,0,"ACTIVE",None,None,10,0,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])

	## look for order closed confirmation
	o_close = EventWatcher.watch(client.ws, 'order_closed')
	await client.ws.publish([0,"oc",[1151718565,None,1548325124885,"tBTCUSD",1548325123435,1548325123548,1,1,"EXCHANGE LIMIT",None,None,None,0,"CANCELED",None,None,10,0,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	close_res = o_close.wait_until_complete()
	assert close_res.amount_orig == 1
	assert float(close_res.amount_filled) == 0
	assert close_res.price == 10
	assert close_res.type == 'EXCHANGE LIMIT'

@pytest.mark.asyncio
async def test_closed_callback_on_submit_order_closed():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	async def c(order):
		client.ws._emit('c1', order)
	callback_wait = EventWatcher.watch(client.ws, 'c1')
	# override cid generation
	client.ws.orderManager._gen_unique_cid = lambda: 123
	await client.ws.submit_order('tBTCUSD', 19000, 0.01, 'EXCHANGE MARKET', onClose=c)
	await client.ws.publish([0,"oc",[123,None,1548262833910,"tBTCUSD",1548262833379,1548262888016,0,-1,"EXCHANGE LIMIT",None,None,None,0,"EXECUTED @ 15980.0(-0.5): was PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	callback_wait.wait_until_complete()


@pytest.mark.asyncio
async def test_confirmed_callback_on_submit_order_closed():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	async def c(order):
		client.ws._emit('c1', order)
	callback_wait = EventWatcher.watch(client.ws, 'c1')
	# override cid generation
	client.ws.orderManager._gen_unique_cid = lambda: 123
	await client.ws.submit_order('tBTCUSD', 19000, 0.01, 'EXCHANGE MARKET', onConfirm=c)
	await client.ws.publish([0,"oc",[123,None,1548262833910,"tBTCUSD",1548262833379,1548262888016,0,-1,"EXCHANGE LIMIT",None,None,None,0,"EXECUTED @ 15980.0(-0.5): was PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	callback_wait.wait_until_complete()

@pytest.mark.asyncio
async def test_confirmed_callback_on_submit_new_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	async def c(order):
		client.ws._emit('c1', order)
	callback_wait = EventWatcher.watch(client.ws, 'c1')
	# override cid generation
	client.ws.orderManager._gen_unique_cid = lambda: 123
	await client.ws.submit_order('tBTCUSD', 19000, 0.01, 'EXCHANGE MARKET', onConfirm=c)
	await client.ws.publish([0,"on",[123,None,1548262833910,"tBTCUSD",1548262833379,1548262833410,-1,-1,"EXCHANGE LIMIT",None,None,None,0,"ACTIVE",None,None,15980,0,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	callback_wait.wait_until_complete()

@pytest.mark.asyncio
async def test_confirmed_callback_on_submit_order_update():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	async def c(order):
		client.ws._emit('c1', order)
	callback_wait = EventWatcher.watch(client.ws, 'c1')
	# override cid generation
	client.ws.orderManager._gen_unique_cid = lambda: 123
	await client.ws.update_order(123, price=100, onConfirm=c)
	await client.ws.publish([0,"ou",[123,None,1548262833910,"tBTCUSD",1548262833379,1548262846964,-0.5,-1,"EXCHANGE LIMIT",None,None,None,0,"PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	callback_wait.wait_until_complete()

@pytest.mark.asyncio
async def test_confirmed_callback_on_submit_cancel_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	async def c(order):
		client.ws._emit('c1', order)
	callback_wait = EventWatcher.watch(client.ws, 'c1')
	# override cid generation
	client.ws.orderManager._gen_unique_cid = lambda: 123
	await client.ws.cancel_order(123, onConfirm=c)
	await client.ws.publish([0,"oc",[123,None,1548262833910,"tBTCUSD",1548262833379,1548262888016,0,-1,"EXCHANGE LIMIT",None,None,None,0,"EXECUTED @ 15980.0(-0.5): was PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	callback_wait.wait_until_complete()

@pytest.mark.asyncio
async def test_confirmed_callback_on_submit_cancel_group_order():
	client = create_stubbed_client()
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	## send auth accepted
	await ws_publish_auth_accepted(client.ws)
	async def c(order):
		client.ws._emit('c1', order)
	callback_wait = EventWatcher.watch(client.ws, 'c1')
	# override cid generation
	client.ws.orderManager._gen_unique_cid = lambda: 123
	await client.ws.cancel_order_group(123, onConfirm=c)
	await client.ws.publish([0,"oc",[1548262833910,123,1548262833910,"tBTCUSD",1548262833379,1548262888016,0,-1,"EXCHANGE LIMIT",None,None,None,0,"EXECUTED @ 15980.0(-0.5): was PARTIALLY FILLED @ 15980.0(-0.5)",None,None,15980,15980,0,0,None,None,None,0,0,None,None,None,"API>BFX",None,None,None]])
	callback_wait.wait_until_complete()
