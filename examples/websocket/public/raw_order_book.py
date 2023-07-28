# python -c "import examples.websocket.public.raw_order_book"
import crcmod

from collections import OrderedDict

from typing import List

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.types import TradingPairRawBook, Checksum
from bfxapi.websocket.subscriptions import Book
from bfxapi.websocket.enums import Channel, Error

class RawOrderBook:
    def __init__(self, symbols: List[str]):
        self.__raw_order_book = {
            symbol: {
                "bids": OrderedDict(), "asks": OrderedDict() 
            } for symbol in symbols
        }
        self.cooldown_flag = False

    def update(self, symbol: str, data: TradingPairRawBook) -> None:
        order_id, price, amount = data.order_id, data.price, data.amount

        kind = "bids" if amount > 0 else "asks"

        if price > 0:
            self.__raw_order_book[symbol][kind][order_id] = {
                "order_id": order_id,
                "price": price, 
                "amount": amount 
            }

        if price == 0:
            if order_id in self.__raw_order_book[symbol][kind]:
                del self.__raw_order_book[symbol][kind][order_id]

    def as_dict(self):
        return self.__raw_order_book

SYMBOLS = [ "tBTCUSD", "tLTCUSD", "tLTCBTC", "tETHUSD", "tETHBTC" ]

raw_order_book = RawOrderBook(symbols=SYMBOLS)

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe(Channel.BOOK, symbol=symbol, prec="R0", enable_checksum=True)

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for pair <{subscription['pair']}>")

@bfx.wss.on("t_raw_book_snapshot")
def on_t_raw_book_snapshot(subscription: Book, snapshot: List[TradingPairRawBook]):
    for data in snapshot:
        raw_order_book.update(subscription["symbol"], data)

@bfx.wss.on("t_raw_book_update")
def on_t_raw_book_update(subscription: Book, data: TradingPairRawBook):
    raw_order_book.update(subscription["symbol"], data)

@bfx.wss.on("checksum_update")
async def on_checksum(subscription: Book, checksum: Checksum):
    data = []
    book = raw_order_book.as_dict()

    # Sort bids by price descending
    # Orders of the same price (for raw books) will need to be sub-sorted by ID
    # in an ascending order (the lower index holds the lower id by numeric value)
    book[subscription["symbol"]]['bids'] = OrderedDict(
        sorted(book[subscription["symbol"]]['bids'].items(), key=lambda t: (-t[1]['price'], t[0]))
    )

    # Sort asks by price ascending
    book[subscription["symbol"]]['asks'] = OrderedDict(
        sorted(book[subscription["symbol"]]['asks'].items(), key=lambda t: (t[1]['price'], t[0]))
    )

    bids_keys = list(book[subscription["symbol"]]['bids'].keys())
    asks_keys = list(book[subscription["symbol"]]['asks'].keys())
    bids_keys_lenght = len(bids_keys)
    asks_keys_lenght = len(asks_keys)

    for i in range(25):
        if i < bids_keys_lenght:
            eid = bids_keys[i]
            pp = book[subscription["symbol"]]['bids'][eid]
            data.extend([pp['order_id'], pp['amount']])
        if i < asks_keys_lenght:
            eid = asks_keys[i]
            pp = book[subscription["symbol"]]['asks'][eid]
            data.extend([pp['order_id'], pp['amount']])

    local_checksum = ":".join(str(value) for value in data)
    crc = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)
    cs_calc = crc(local_checksum.encode())

    print('Local checksum: ', cs_calc, 'Remote checksum: ', checksum.value)

    if cs_calc == checksum.value:
        print('Checksum is ok')
        raw_order_book.cooldown_flag = False
    else:
        if raw_order_book.cooldown_flag is False: # avoid race conditions
            print('Checksum mismatch - Restarting all books')
            raw_order_book.cooldown_flag = True
            await bfx.wss.unsubscribe(Channel.BOOK)
            
            for symbol in SYMBOLS:
                await bfx.wss.subscribe(Channel.BOOK, symbol=symbol, prec="R0", enable_checksum=True)

bfx.wss.run()
