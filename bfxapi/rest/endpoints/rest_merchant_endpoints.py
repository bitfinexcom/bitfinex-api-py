from typing import TypedDict, List, Union, Literal, Optional

from decimal import Decimal

from .. types import *
from .. middleware import Middleware
from ...utils.camel_and_snake_case_helpers import to_snake_case_keys, to_camel_case_keys

_CustomerInfo = TypedDict("_CustomerInfo", {
    "nationality": str, "resid_country": str, "resid_city": str, 
    "resid_zip_code": str, "resid_street": str, "resid_building_no": str, 
    "full_name": str, "email": str, "tos_accepted": bool
})

class RestMerchantEndpoints(Middleware):
    def submit_invoice(self, amount: Union[Decimal, float, str], currency: str, order_id: str, 
                       customer_info: _CustomerInfo, pay_currencies: List[str], duration: Optional[int] = None,
                       webhook: Optional[str] = None, redirect_url: Optional[str] = None) -> InvoiceSubmission:
        body = to_camel_case_keys({
            "amount": amount, "currency": currency, "order_id": order_id,
            "customer_info": customer_info, "pay_currencies": pay_currencies, "duration": duration,
            "webhook": webhook, "redirect_url": redirect_url
        })

        data = to_snake_case_keys(self._POST("auth/w/ext/pay/invoice/create", body=body))
        
        return InvoiceSubmission.parse(data)

    def get_invoices(self, id: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[InvoiceSubmission]:
        return [ InvoiceSubmission.parse(sub_data) for sub_data in to_snake_case_keys(self._POST("auth/r/ext/pay/invoices", body={
            "id": id, "start": start, "end": end, 
            "limit": limit
        })) ]

    def get_invoice_count_stats(self, status: Literal["CREATED", "PENDING", "COMPLETED", "EXPIRED"], format: str) -> List[InvoiceStats]:
        return [ InvoiceStats(**sub_data) for sub_data in self._POST("auth/r/ext/pay/invoice/stats/count", body={ "status": status, "format": format }) ]

    def get_invoice_earning_stats(self, currency: str, format: str) -> List[InvoiceStats]:
        return [ InvoiceStats(**sub_data) for sub_data in self._POST("auth/r/ext/pay/invoice/stats/earning", body={ "currency": currency, "format": format }) ]

    def complete_invoice(self, id: str, pay_currency: str, deposit_id: Optional[int] = None, ledger_id: Optional[int] = None) -> InvoiceSubmission:
        return InvoiceSubmission.parse(to_snake_case_keys(self._POST("auth/w/ext/pay/invoice/complete", body={
            "id": id, "payCcy": pay_currency, "depositId": deposit_id, 
            "ledgerId": ledger_id
        })))

    def expire_invoice(self, id: str) -> InvoiceSubmission:
        return InvoiceSubmission.parse(to_snake_case_keys(self._POST("auth/w/ext/pay/invoice/expire", body={ "id": id })))

    def get_currency_conversion_list(self) -> List[CurrencyConversion]:
        return [
            CurrencyConversion(
                base_currency=sub_data["baseCcy"], 
                convert_currency=sub_data["convertCcy"], 
                created=sub_data["created"]
            ) for sub_data in self._POST("auth/r/ext/pay/settings/convert/list")
        ]

    def add_currency_conversion(self, base_currency: str, convert_currency: str) -> bool:
        return bool(self._POST("auth/w/ext/pay/settings/convert/create", body={
            "baseCcy": base_currency,
            "convertCcy": convert_currency
        }))

    def remove_currency_conversion(self, base_currency: str, convert_currency: str) -> bool:
        return bool(self._POST("auth/w/ext/pay/settings/convert/remove", body={
            "baseCcy": base_currency,
            "convertCcy": convert_currency
        }))