
class Flags:
    """
    Enum used to index the available flags used in the authentication
    websocket packet
    """
    DEC_S = 9
    TIME_S = 32
    TIMESTAMP = 32768
    SEQ_ALL = 65536
    CHECKSUM = 131072

    strings = {
        9: 'DEC_S',
        32: 'TIME_S',
        32768: 'TIMESTAMP',
        65536: 'SEQ_ALL',
        131072: 'CHECKSUM'
    }

class WSChannels:
    """
    Enum used to index all available subscribable channels
    """
    BOOK = 'book'
    CANDLES = 'candles'
    STATUS = 'status'
    TICKER = 'ticker'
    TRADES = 'trades'


class WSEvents:
    """
    Enum used to index all available websocket event emitter event
    """
    ALL = 'all'
    AUTHENTICATED = 'authenticated'
    BALANCE_UPDATE = 'balance_update'
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    DONE = 'done'
    ERROR = 'error'
    FUNDING_CREDIT_SNAPSHOT = 'funding_credit_snapshot'
    FUNDING_INFO_UPDATE = 'funding_info_update'
    FUNDING_LOAN_SNAPSHOT = 'funding_loan_snapshot'
    FUNDING_OFFER_SNAPSHOT = 'funding_offer_snapshot'
    HEART_BEAT = 'heart_beat'
    MARGIN_INFO_UPDATE = 'margin_info_update'
    NEW_CANDLE = 'new_candle'
    NEW_FUNDING_TICKER = 'new_funding_ticker'
    NEW_TICKER = 'new_ticker'
    NEW_TRADE = 'new_trade'
    NEW_TRADE = 'new_trade'
    NEW_TRADING_TICKER = 'new_trading_ticker'
    NEW_USER_TRADE = 'new_user_trade'
    NOTIFICATION = 'notification'
    ORDER_BOOK_SNAPSHOT = 'order_book_snapshot'
    ORDER_BOOK_UPDATE = 'order_book_update'
    ORDER_CLOSED = 'order_closed'
    ORDER_CONFIRMED = 'order_confirmed'
    ORDER_NEW = 'order_new'
    ORDER_SNAPSHOT = 'order_snapshot'
    ORDER_UPDATE = 'order_update'
    POSITION_CLOSE = 'position_close'
    POSITION_NEW = 'position_new'
    POSITION_SNAPSHOT = 'position_snapshot'
    POSITION_UPDATE = 'position_update'
    SEED_CANDLE = 'seed_candle'
    SEED_TRADE = 'seed_trade'
    STATUS_UPDATE = 'status_update'
    STOPPED = 'stopped'
    SUBSCRIBED = 'subscribed'
    TRADE_UPDATE = 'trade_update'
    UNSUBSCRIBED = 'unsubscribed'
    USER_TRADE_UPDATE = 'user_trade_update'
    WALLET_SNAPSHOT = 'wallet_snapshot'
    WALLET_UPDATE = 'wallet_update'

ERRORS = {
    10000: 'Unknown event',
    10001: 'Generic error',
    10008: 'Concurrency error',
    10020: 'Request parameters error',
    10050: 'Configuration setup failed',
    10100: 'Failed authentication',
    10111: 'Error in authentication request payload',
    10112: 'Error in authentication request signature',
    10113: 'Error in authentication request encryption',
    10114: 'Error in authentication request nonce',
    10200: 'Error in un-authentication request',
    10300: 'Subscription Failed (generic)',
    10301: 'Already Subscribed',
    10305: 'Reached limit of open channels',
    10302: 'Unknown channel',
    10400: 'Subscription Failed (generic)',
    10401: 'Not subscribed',
    11000: 'Not ready, try again later',
    20000: 'User is invalid!',
    20051: 'Websocket server stopping',
    20060: 'Websocket server resyncing',
    20061: 'Websocket server resync complete'
}