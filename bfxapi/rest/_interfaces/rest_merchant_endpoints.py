from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, Union

from bfxapi.rest._interface import Interface
from bfxapi.types import (
    CurrencyConversion,
    InvoicePage,
    InvoiceStats,
    InvoiceSubmission,
    MerchantDeposit,
    MerchantUnlinkedDeposit,
)


class RestMerchantEndpoints(Interface):
    def submit_invoice(
        self,
        amount: Union[str, float, Decimal],
        currency: str,
        order_id: str,
        customer_info: Dict[str, Any],
        pay_currencies: List[str],
        *,
        duration: Optional[int] = None,
        webhook: Optional[str] = None,
        redirect_url: Optional[str] = None,
    ) -> InvoiceSubmission:
        body = {
            "amount": amount,
            "currency": currency,
            "orderId": order_id,
            "customerInfo": customer_info,
            "payCurrencies": pay_currencies,
            "duration": duration,
            "webhook": webhook,
            "redirectUrl": redirect_url,
        }

        data = self._m.post("auth/w/ext/pay/invoice/create", body=body)

        return InvoiceSubmission.parse(data)

    def get_invoices(
        self,
        *,
        id: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[InvoiceSubmission]:
        body = {"id": id, "start": start, "end": end, "limit": limit}

        data = self._m.post("auth/r/ext/pay/invoices", body=body)

        return [InvoiceSubmission.parse(sub_data) for sub_data in data]

    def get_invoices_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        sort: Literal["asc", "desc"] = "asc",
        sort_field: Literal["t", "amount", "status"] = "t",
        *,
        status: Optional[
            List[Literal["CREATED", "PENDING", "COMPLETED", "EXPIRED"]]
        ] = None,
        fiat: Optional[List[str]] = None,
        crypto: Optional[List[str]] = None,
        id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> InvoicePage:
        body = {
            "page": page,
            "pageSize": page_size,
            "sort": sort,
            "sortField": sort_field,
            "status": status,
            "fiat": fiat,
            "crypto": crypto,
            "id": id,
            "orderId": order_id,
        }

        data = self._m.post("auth/r/ext/pay/invoices/paginated", body=body)

        return InvoicePage.parse(data)

    def get_invoice_count_stats(
        self, status: Literal["CREATED", "PENDING", "COMPLETED", "EXPIRED"], format: str
    ) -> List[InvoiceStats]:
        return [
            InvoiceStats(**sub_data)
            for sub_data in self._m.post(
                "auth/r/ext/pay/invoice/stats/count",
                body={"status": status, "format": format},
            )
        ]

    def get_invoice_earning_stats(
        self, currency: str, format: str
    ) -> List[InvoiceStats]:
        return [
            InvoiceStats(**sub_data)
            for sub_data in self._m.post(
                "auth/r/ext/pay/invoice/stats/earning",
                body={"currency": currency, "format": format},
            )
        ]

    def complete_invoice(
        self,
        id: str,
        pay_currency: str,
        *,
        deposit_id: Optional[int] = None,
        ledger_id: Optional[int] = None,
    ) -> InvoiceSubmission:
        body = {
            "id": id,
            "payCcy": pay_currency,
            "depositId": deposit_id,
            "ledgerId": ledger_id,
        }

        data = self._m.post("auth/w/ext/pay/invoice/complete", body=body)

        return InvoiceSubmission.parse(data)

    def expire_invoice(self, id: str) -> InvoiceSubmission:
        body = {"id": id}

        data = self._m.post("auth/w/ext/pay/invoice/expire", body=body)

        return InvoiceSubmission.parse(data)

    def get_currency_conversion_list(self) -> List[CurrencyConversion]:
        return [
            CurrencyConversion(**sub_data)
            for sub_data in self._m.post("auth/r/ext/pay/settings/convert/list")
        ]

    def add_currency_conversion(self, base_ccy: str, convert_ccy: str) -> bool:
        return bool(
            self._m.post(
                "auth/w/ext/pay/settings/convert/create",
                body={"baseCcy": base_ccy, "convertCcy": convert_ccy},
            )
        )

    def remove_currency_conversion(self, base_ccy: str, convert_ccy: str) -> bool:
        return bool(
            self._m.post(
                "auth/w/ext/pay/settings/convert/remove",
                body={"baseCcy": base_ccy, "convertCcy": convert_ccy},
            )
        )

    def set_merchant_settings(self, key: str, val: Any) -> bool:
        return bool(
            self._m.post("auth/w/ext/pay/settings/set", body={"key": key, "val": val})
        )

    def get_merchant_settings(self, key: str) -> Any:
        return self._m.post("auth/r/ext/pay/settings/get", body={"key": key})

    def list_merchant_settings(
        self, keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        return self._m.post("auth/r/ext/pay/settings/list", body={"keys": keys or []})

    def get_deposits(
        self,
        start: int,
        to: int,
        *,
        ccy: Optional[str] = None,
        unlinked: Optional[bool] = None,
    ) -> List[MerchantDeposit]:
        body = {"from": start, "to": to, "ccy": ccy, "unlinked": unlinked}

        data = self._m.post("auth/r/ext/pay/deposits", body=body)

        return [MerchantDeposit(**sub_data) for sub_data in data]

    def get_unlinked_deposits(
        self, ccy: str, *, start: Optional[int] = None, end: Optional[int] = None
    ) -> List[MerchantUnlinkedDeposit]:
        body = {"ccy": ccy, "start": start, "end": end}

        data = self._m.post("/auth/r/ext/pay/deposits/unlinked", body=body)

        return [MerchantUnlinkedDeposit(**sub_data) for sub_data in data]
