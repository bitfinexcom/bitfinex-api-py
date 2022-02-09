def _parse_candle(cData, symbol, tf):
    return {
        'mts': cData[0],
        'open': cData[1],
        'close': cData[2],
        'high': cData[3],
        'low': cData[4],
        'volume': cData[5],
        'symbol': symbol,
        'tf': tf
    }


def _parse_trade_snapshot_item(tData, symbol):
    return {
        'mts': tData[3],
        'price': tData[4],
        'amount': tData[5],
        'symbol': symbol
    }


def _parse_trade(tData, symbol):
    return {
        'mts': tData[1],
        'price': tData[3],
        'amount': tData[2],
        'symbol': symbol
    }


def _parse_user_trade(tData):
    return {
        'id': tData[0],
        'symbol': tData[1],
        'mts_create': tData[2],
        'order_id': tData[3],
        'exec_amount': tData[4],
        'exec_price': tData[5],
        'order_type': tData[6],
        'order_price': tData[7],
        'maker': tData[8],
        'cid': tData[11],
    }


def _parse_user_trade_update(tData):
    return {
        'id': tData[0],
        'symbol': tData[1],
        'mts_create': tData[2],
        'order_id': tData[3],
        'exec_amount': tData[4],
        'exec_price': tData[5],
        'order_type': tData[6],
        'order_price': tData[7],
        'maker': tData[8],
        'fee': tData[9],
        'fee_currency': tData[10],
        'cid': tData[11],
    }


def _parse_deriv_status_update(sData, symbol):
    return {
            'symbol': symbol,
            'status_type': 'deriv',
            'mts': sData[0],
            # placeholder
            'deriv_price': sData[2],
            'spot_price': sData[3],
            # placeholder
            'insurance_fund_balance': sData[5],
            # placeholder
            # placeholder
            'funding_accrued': sData[8],
            'funding_step': sData[9],
            # placeholder
        }