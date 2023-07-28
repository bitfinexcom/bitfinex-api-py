# python -c "import examples.websocket.public.order_book"
import crcmod

from collections import OrderedDict

from typing import List

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.types import TradingPairBook, Checksum
from bfxapi.websocket.subscriptions import Book
from bfxapi.websocket.enums import Channel, Error

class OrderBook:
    def __init__(self, symbols: List[str]):
        self.__order_book = {
            symbol: {
                "bids": OrderedDict(), "asks": OrderedDict() 
            } for symbol in symbols
        }
        self.cooldown_flag = False

    def update(self, symbol: str, data: TradingPairBook) -> None:
        price, count, amount = data.price, data.count, data.amount

        kind = "bids" if amount > 0 else "asks"

        if count > 0:
            self.__order_book[symbol][kind][price] = {
                "price": price, 
                "count": count,
                "amount": amount 
            }

        if count == 0:
            if price in self.__order_book[symbol][kind]:
                del self.__order_book[symbol][kind][price]

    def as_dict(self):
        return self.__order_book

SYMBOLS = [ "tBTCUSD", "tLTCUSD", "tLTCBTC", "tETHUSD", "tETHBTC" ]

order_book = OrderBook(symbols=SYMBOLS)

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe(Channel.BOOK, symbol=symbol, enable_checksum=True)

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for pair <{subscription['pair']}>")

@bfx.wss.on("t_book_snapshot")
def on_t_book_snapshot(subscription: Book, snapshot: List[TradingPairBook]):
    for data in snapshot:
        order_book.update(subscription["symbol"], data)

@bfx.wss.on("t_book_update")
def on_t_book_update(subscription: Book, data: TradingPairBook):
    order_book.update(subscription["symbol"], data)

@bfx.wss.on("checksum_update")
async def on_checksum(subscription: Book, checksum: Checksum):
    data = []
    book = order_book.as_dict()

    # Sort bids by price descending
    book[subscription["symbol"]]['bids'] = OrderedDict(
        sorted(book[subscription["symbol"]]['bids'].items(), key=lambda t: t[0], reverse=True)
    )

    # Sort asks by price ascending
    book[subscription["symbol"]]['asks'] = OrderedDict(
        sorted(book[subscription["symbol"]]['asks'].items(), key=lambda t: t[0])
    )

    bids_keys = list(book[subscription["symbol"]]['bids'].keys())
    asks_keys = list(book[subscription["symbol"]]['asks'].keys())
    bids_keys_lenght = len(bids_keys)
    asks_keys_lenght = len(asks_keys)

    for i in range(25):
        if i < bids_keys_lenght:
            eid = bids_keys[i]
            pp = book[subscription["symbol"]]['bids'][eid]
            data.extend([pp['price'], pp['amount']])
        if i < asks_keys_lenght:
            eid = asks_keys[i]
            pp = book[subscription["symbol"]]['asks'][eid]
            data.extend([pp['price'], pp['amount']])

    local_checksum = ":".join(str(value) for value in data)
    crc = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)
    cs_calc = crc(local_checksum.encode())

    print('Local checksum: ', cs_calc, 'Remote checksum: ', checksum.value)

    if cs_calc == checksum.value:
        print('Checksum is ok')
        order_book.cooldown_flag = False
    else:
        print('Checksum mismatch - Restarting all books')
        if order_book.cooldown_flag is False: # avoid race conditions
            order_book.cooldown_flag = True
            await bfx.wss.unsubscribe(Channel.BOOK)
            
            for symbol in SYMBOLS:
                await bfx.wss.subscribe(Channel.BOOK, symbol=symbol, enable_checksum=True)


bfx.wss.run()
