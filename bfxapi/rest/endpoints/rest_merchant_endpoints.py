from typing import TypedDict, Dict, List, Union, Literal, Optional, Any

from decimal import Decimal

from .. types import \
    InvoiceSubmission, InvoicePage, InvoiceStats, \
    CurrencyConversion, MerchantDeposit, MerchantUnlinkedDeposit

from .. enums import MerchantSettingsKey

from .. middleware import Middleware

from ...utils.camel_and_snake_case_helpers import to_snake_case_keys, to_camel_case_keys

_CustomerInfo = TypedDict("_CustomerInfo", {
    "nationality": str, "resid_country": str, "resid_city": str, 
    "resid_zip_code": str, "resid_street": str, "resid_building_no": str, 
    "full_name": str, "email": str, "tos_accepted": bool
})

class RestMerchantEndpoints(Middleware):
    #pylint: disable-next=too-many-arguments
    def submit_invoice(self,
                       amount: Union[Decimal, float, str],
                       currency: str,
                       order_id: str,
                       customer_info: _CustomerInfo,
                       pay_currencies: List[str],
                       *,
                       duration: Optional[int] = None,
                       webhook: Optional[str] = None,
                       redirect_url: Optional[str] = None) -> InvoiceSubmission:
        body = to_camel_case_keys({
            "amount": amount, "currency": currency, "order_id": order_id,
            "customer_info": customer_info, "pay_currencies": pay_currencies, "duration": duration,
            "webhook": webhook, "redirect_url": redirect_url
        })

        data = to_snake_case_keys(self._post("auth/w/ext/pay/invoice/create", body=body))

        return InvoiceSubmission.parse(data)

    def get_invoices(self,
                     *,
                     id: Optional[str] = None,
                     start: Optional[str] = None,
                     end: Optional[str] = None,
                     limit: Optional[int] = None) -> List[InvoiceSubmission]:
        body = {
            "id": id, "start": start, "end": end, 
            "limit": limit
        }

        response = self._post("auth/r/ext/pay/invoices", body=body)

        return [ InvoiceSubmission.parse(sub_data) for sub_data in to_snake_case_keys(response) ]

    def get_invoices_paginated(self,
                               page: int = 1,
                               page_size: int = 10,
                               sort: Literal["asc", "desc"] = "asc",
                               sort_field: Literal["t", "amount", "status"] = "t",
                               *,
                               status: Optional[List[Literal["CREATED", "PENDING", "COMPLETED", "EXPIRED"]]] = None,
                               fiat: Optional[List[str]] = None,
                               crypto: Optional[List[str]] = None,
                               id: Optional[str] = None,
                               order_id: Optional[str] = None) -> InvoicePage:
        body = to_camel_case_keys({
            "page": page, "page_size": page_size, "sort": sort,
            "sort_field": sort_field, "status": status, "fiat": fiat,
            "crypto": crypto, "id": id, "order_id": order_id
        })

        data = to_snake_case_keys(self._post("auth/r/ext/pay/invoices/paginated", body=body))

        return InvoicePage.parse(data)

    def get_invoice_count_stats(self,
                                status: Literal["CREATED", "PENDING", "COMPLETED", "EXPIRED"],
                                format: str) -> List[InvoiceStats]:
        return [ InvoiceStats(**sub_data) for sub_data in \
            self._post("auth/r/ext/pay/invoice/stats/count", body={ "status": status, "format": format }) ]

    def get_invoice_earning_stats(self,
                                  currency: str,
                                  format: str) -> List[InvoiceStats]:
        return [ InvoiceStats(**sub_data) for sub_data in \
            self._post("auth/r/ext/pay/invoice/stats/earning", body={ "currency": currency, "format": format }) ]

    def complete_invoice(self,
                         id: str,
                         pay_currency: str,
                         *,
                         deposit_id: Optional[int] = None,
                         ledger_id: Optional[int] = None) -> InvoiceSubmission:
        return InvoiceSubmission.parse(to_snake_case_keys(self._post("auth/w/ext/pay/invoice/complete", body={
            "id": id, "payCcy": pay_currency, "depositId": deposit_id, 
            "ledgerId": ledger_id
        })))

    def expire_invoice(self, id: str) -> InvoiceSubmission:
        body = { "id": id }
        response = self._post("auth/w/ext/pay/invoice/expire", body=body)
        return InvoiceSubmission.parse(to_snake_case_keys(response))

    def get_currency_conversion_list(self) -> List[CurrencyConversion]:
        return [
            CurrencyConversion(
                base_currency=sub_data["baseCcy"],
                convert_currency=sub_data["convertCcy"],
                created=sub_data["created"]
            ) for sub_data in self._post("auth/r/ext/pay/settings/convert/list")
        ]

    def add_currency_conversion(self,
                                base_currency: str,
                                convert_currency: str) -> bool:
        return bool(self._post("auth/w/ext/pay/settings/convert/create", body={
            "baseCcy": base_currency,
            "convertCcy": convert_currency
        }))

    def remove_currency_conversion(self,
                                   base_currency: str,
                                   convert_currency: str) -> bool:
        return bool(self._post("auth/w/ext/pay/settings/convert/remove", body={
            "baseCcy": base_currency,
            "convertCcy": convert_currency
        }))

    def set_merchant_settings(self,
                              key: MerchantSettingsKey,
                              val: Any) -> bool:
        return bool(self._post("auth/w/ext/pay/settings/set", body={ "key": key, "val": val }))

    def get_merchant_settings(self, key: MerchantSettingsKey) -> Any:
        return self._post("auth/r/ext/pay/settings/get", body={ "key": key })

    def list_merchant_settings(self, keys: List[MerchantSettingsKey] = []) -> Dict[MerchantSettingsKey, Any]:
        return self._post("auth/r/ext/pay/settings/list", body={ "keys": keys })

    def get_deposits(self,
                     start: int,
                     end: int,
                     *,
                     ccy: Optional[str] = None,
                     unlinked: Optional[bool] = None) -> List[MerchantDeposit]:
        body = { "from": start, "to": end, "ccy": ccy, "unlinked": unlinked }
        response = self._post("auth/r/ext/pay/deposits", body=body)
        return [ MerchantDeposit(**sub_data) for sub_data in to_snake_case_keys(response) ]

    def get_unlinked_deposits(self,
                              ccy: str,
                              *,
                              start: Optional[int] = None,
                              end: Optional[int] = None) -> List[MerchantUnlinkedDeposit]:
        body = { "ccy": ccy, "start": start, "end": end }
        response = self._post("/auth/r/ext/pay/deposits/unlinked", body=body)
        return [ MerchantUnlinkedDeposit(**sub_data) for sub_data in to_snake_case_keys(response) ]
