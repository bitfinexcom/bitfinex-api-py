import pytest
from .helpers import create_stubbed_client, ws_publish_connection_init, ws_publish_conf_accepted

@pytest.mark.asyncio
async def test_checksum_generation():
    client = create_stubbed_client()
    symbol = "tXRPBTC"
    # publish connection created message
    await ws_publish_connection_init(client.ws)
    # publish checksum flag accepted
    await ws_publish_conf_accepted(client.ws, 131072)
    # subscribe to order book
    await client.ws.subscribe('book', symbol)
    ## send subscription accepted
    chanId = 123
    await client.ws.publish({"event":"subscribed","channel":"book","chanId": chanId,"symbol": symbol,"prec":"P0","freq":"F0","len":"25","pair": symbol})
    ## send orderbook snapshot
    await client.ws.publish("""[123, [[0.0000886,1,1060.55466114],[0.00008859,1,1000],[0.00008858,1,2713.47159343],[0.00008857,1,4276.92870916],[0.00008856,2,6764.75562319],
    [0.00008854,1,5641.48532401],[0.00008853,1,2255.92632223],[0.0000885,1,2256.69584601],[0.00008848,2,3630.3],[0.00008845,1,28195.70625766],
    [0.00008844,1,15571.7],[0.00008843,1,2500],[0.00008841,1,64196.16117814],[0.00008838,1,7500],[0.00008837,2,2764.12999012],[0.00008834,2,10886.476298],
    [0.00008831,1,20000],[0.0000883,1,1000],[0.00008829,2,2517.22175358],[0.00008828,1,450.45],[0.00008827,1,13000],[0.00008824,1,1500],[0.0000882,1,300],
    [0.00008817,1,3000],[0.00008816,1,100],[0.00008864,1,-481.8549041],[0.0000887,2,-2141.77009092],[0.00008871,1,-2256.45433182],[0.00008872,1,-2707.58122743],
    [0.00008874,1,-5640.31794092],[0.00008876,1,-29004.93294912],[0.00008878,1,-2500],[0.0000888,1,-20000],[0.00008881,2,-2880.15595827],[0.00008882,1,-27705.42933984],
    [0.00008883,1,-4509.83708214],[0.00008884,1,-1500],[0.00008885,1,-2500],[0.00008888,1,-902.91405442],[0.00008889,1,-900],[0.00008891,1,-7500],
    [0.00008894,1,-775.08564697],[0.00008896,1,-150],[0.00008899,3,-11628.02590049],[0.000089,2,-1299.7],[0.00008902,2,-4841.8],[0.00008904,3,-25320.46250083],
    [0.00008909,1,-14000],[0.00008913,1,-123947.999],[0.00008915,2,-28019.6]]]""", is_json=False)
    ## send some more price updates
    await client.ws.publish("[{},[0.00008915,0,-1]]".format(chanId), is_json=False)
    await client.ws.publish("[{},[0.00008837,1,56.54876269]]".format(chanId), is_json=False)
    await client.ws.publish("[{},[0.00008873,1,-15699.9]]".format(chanId), is_json=False)
    ## check checksum is the same as expected
    expected_checksum = 30026640
    actual_checksum = client.ws.orderBooks[symbol].checksum()
    assert expected_checksum == actual_checksum

@pytest.mark.asyncio
async def test_checksum_really_samll_numbers_generation():
    client = create_stubbed_client()
    symbol = "tVETBTC"
    # publish connection created message
    await ws_publish_connection_init(client.ws)
    # publish checksum flag accepted
    await ws_publish_conf_accepted(client.ws, 131072)
    # subscribe to order book
    await client.ws.subscribe('book', symbol)
    ## send subscription accepted
    chanId = 123
    await client.ws.publish({"event":"subscribed","channel":"book","chanId": chanId,"symbol": symbol,"prec":"P0","freq":"F0","len":"25","pair": symbol})
    ## send orderbook snapshot
    await client.ws.publish("""[123, [[0.00000121,5,249013.0209708],[0.0000012,6,518315.33310128],[0.00000119,4,566200.89],[0.00000118,2,260000],[0.00000117,1,100000],
    [0.00000116,2,160000],[0.00000114,1,60000],[0.00000113,2,198500],[0.00000112,1,60000],[0.0000011,1,60000],[0.00000106,2,113868.87735849],[0.00000105,2,105000],
    [0.00000103,1,3000],[0.00000102,2,105000],[0.00000101,2,202970],[0.000001,2,21000],[7e-7,1,10000],[6.6e-7,1,10000],[6e-7,1,100000],[4.9e-7,1,10000],[2.5e-7,1,2000],
    [6e-8,1,100000],[5e-8,1,200000],[1e-8,4,640000],[0.00000122,7,-312043.19],[0.00000123,6,-415094.8939744],[0.00000124,5,-348181.23],[0.00000125,1,-12000],
    [0.00000126,2,-143872.31],[0.00000127,1,-5000],[0.0000013,1,-5000],[0.00000134,1,-8249.18938656],[0.00000135,2,-230043.1337899],[0.00000136,1,-13161.25184766],
    [0.00000145,1,-2914],[0.0000015,3,-54448.5],[0.00000152,2,-5538.54849594],[0.00000153,1,-62691.75475079],[0.00000159,1,-2914],[0.0000016,1,-52631.10296831],
    [0.00000164,1,-4000],[0.00000166,1,-3831.46784605],[0.00000171,1,-14575.17730379],[0.00000174,1,-3124.81815395],[0.0000018,1,-18000],[0.00000182,1,-16000],
    [0.00000186,1,-4000],[0.00000189,1,-10000.686624],[0.00000191,1,-14500]]]""", is_json=False)
    ## send some more price updates
    await client.ws.publish("[{},[0.00000121,4,228442.6609708]]".format(chanId), is_json=False)
    await client.ws.publish("[{},[0.00000121,6,304023.8109708]]".format(chanId), is_json=False)
    # await client.ws.publish("[{},[0.00008873,1,-15699.9]]".format(chanId), is_json=False)
    ## check checksum is the same as expected
    expected_checksum = 1770440002
    actual_checksum = client.ws.orderBooks[symbol].checksum()
    assert expected_checksum == actual_checksum
