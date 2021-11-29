import pytest
import json
from .helpers import (create_stubbed_client, ws_publish_connection_init, EventWatcher)

@pytest.mark.asyncio
async def test_submit_subscribe():
	client = create_stubbed_client()
	symb = 'tXRPBTC'
	# publish connection created message
	await ws_publish_connection_init(client.ws)

	# Create new subscription to orderbook
	await client.ws.subscribe('book', symb)
	last_sent = client.ws.get_last_sent_item()
	sent_sub = json.loads(last_sent['data'])
	# {'time': 1548327054030, 'data': '{"event": "subscribe", "channel": "book", "symbol": "tXRPBTC"}'}
	assert sent_sub['event'] == "subscribe"
	assert sent_sub['channel'] == "book"
	assert sent_sub['symbol'] == symb

	# create new subscription to trades
	await client.ws.subscribe('trades', symb)
	last_sent = client.ws.get_last_sent_item()
	sent_sub = json.loads(last_sent['data'])
	# {'event': 'subscribe', 'channel': 'trades', 'symbol': 'tBTCUSD'}
	assert sent_sub['event'] == 'subscribe'
	assert sent_sub['channel'] == 'trades'
	assert sent_sub['symbol'] == symb

	# create new subscription to candles
	await client.ws.subscribe('candles', symb, timeframe='1m')
	last_sent = client.ws.get_last_sent_item()
	sent_sub = json.loads(last_sent['data'])
	#{'event': 'subscribe', 'channel': 'candles', 'symbol': 'tBTCUSD', 'key': 'trade:1m:tBTCUSD'}
	assert sent_sub['event'] == 'subscribe'
	assert sent_sub['channel'] == 'candles'
	assert sent_sub['key'] == 'trade:1m:{}'.format(symb)

@pytest.mark.asyncio
async def test_event_subscribe():
	client = create_stubbed_client()
	symb = 'tXRPBTC'
	pair = 'XRPBTC'
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	# create a new subscription
	await client.ws.subscribe('trades', symb)
	# announce subscription was successful
	sub_watch = EventWatcher.watch(client.ws, 'subscribed')
	await client.ws.publish({"event":"subscribed","channel":"trades","chanId":2,"symbol":symb,"pair":pair})
	s_res = sub_watch.wait_until_complete()
	assert s_res.channel_name == 'trades'
	assert s_res.symbol == symb
	assert s_res.is_subscribed_bool == True
	assert s_res.chan_id == 2

@pytest.mark.asyncio
async def test_submit_unsubscribe():
	client = create_stubbed_client()
	symb = 'tXRPBTC'
	pair = 'XRPBTC'
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	# create new subscription to trades
	await client.ws.subscribe('trades', symb)
	 # announce subscription was successful
	sub_watch = EventWatcher.watch(client.ws, 'subscribed')
	await client.ws.publish({"event":"subscribed","channel":"trades","chanId":2,"symbol":symb,"pair":pair})
	s_res = sub_watch.wait_until_complete()
	# unsubscribe from channel
	await s_res.unsubscribe()
	last_sent = client.ws.get_last_sent_item()
	sent_unsub = json.loads(last_sent['data'])
	# {'event': 'unsubscribe', 'chanId': 2}
	assert sent_unsub['event'] == 'unsubscribe'
	assert sent_unsub['chanId'] == 2

@pytest.mark.asyncio
async def test_event_unsubscribe():
	client = create_stubbed_client()
	symb = 'tXRPBTC'
	pair = 'XRPBTC'
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	# create new subscription to trades
	await client.ws.subscribe('trades', symb)
	 # announce subscription was successful
	sub_watch = EventWatcher.watch(client.ws, 'subscribed')
	await client.ws.publish({"event":"subscribed","channel":"trades","chanId":2,"symbol":symb,"pair":pair})
	s_res = sub_watch.wait_until_complete()
	# unsubscribe from channel
	await s_res.unsubscribe()
	last_sent = client.ws.get_last_sent_item()
	sent_unsub = json.loads(last_sent['data'])
	
	# publish confirmation of unsubscribe
	unsub_watch = EventWatcher.watch(client.ws, 'unsubscribed')
	await client.ws.publish({"event":"unsubscribed","status":"OK","chanId":2})
	unsub_res = unsub_watch.wait_until_complete()
	assert s_res.channel_name == 'trades'
	assert s_res.symbol == symb
	assert s_res.is_subscribed_bool == False
	assert s_res.chan_id == 2

@pytest.mark.asyncio
async def test_submit_resubscribe():
	client = create_stubbed_client()
	symb = 'tXRPBTC'
	pair = 'XRPBTC'
	# publish connection created message
	await ws_publish_connection_init(client.ws)
	# request two new subscriptions
	await client.ws.subscribe('book', symb)
	await client.ws.subscribe('trades', symb)
	# confirm subscriptions
	await client.ws.publish({"event":"subscribed","channel":"trades","chanId":2,"symbol":symb,"pair":pair})
	await client.ws.publish({"event":"subscribed","channel":"book","chanId":3,"symbol":symb,"prec":"P0","freq":"F0","len":"25","pair":pair})
	# call resubscribe all
	await client.ws.resubscribe_all()
	## assert that 2 unsubscribe requests were sent
	last_sent = client.ws.get_sent_items()[-2:]
	for i in last_sent:
		data = json.loads(i['data'])
		assert data['event'] == 'unsubscribe'
		assert (data['chanId'] == 2 or data['chanId'] == 3)
	## confirm unsubscriptions
	await client.ws.publish({"event":"unsubscribed","status":"OK","chanId":2})
	await client.ws.publish({"event":"unsubscribed","status":"OK","chanId":3})

	## confirm subscriptions
	# await client.ws.publish({"event":"subscribed","channel":"trades","chanId":2,"symbol":symb,"pair":pair})
	# await client.ws.publish({"event":"subscribed","channel":"book","chanId":3,"symbol":symb,"prec":"P0","freq":"F0","len":"25","pair":pair})
	# wait for emit of event
	n_last_sent = client.ws.get_sent_items()[-2:]
	for i in n_last_sent:
		data = json.loads(i['data'])
		# print (data)
		assert data['event'] == 'subscribe'
		assert (data['channel'] == 'book' or data['channel'] == 'trades')
		assert data['symbol'] == symb
