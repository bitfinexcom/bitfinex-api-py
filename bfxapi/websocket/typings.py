from typing import TypedDict, List, Optional

class BalanceUpdateStream(TypedDict):
    AUM: float
    AUM_NET: float

class WalletUpdateStream(TypedDict):
    WALLET_TYPE: str
    CURRENCY: str
    BALANCE: float
    UNSETTLED_INTEREST: float
    BALANCE_AVAILABLE: Optional[float]
    DESCRIPTION: str
    META: dict

WalletSnapshotStream = List[WalletUpdateStream]