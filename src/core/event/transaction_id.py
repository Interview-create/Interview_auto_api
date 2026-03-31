from datetime import datetime
from entity.request_entity import TestCase


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 transaction_id 替換成新的 值,只有外部現金網登入會用到。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    try:

        if not isRequest:
            return

        if not case.payload.get("transaction_id", False):
            return

        transaction = str(int(datetime.now().timestamp()))
        transaction_id = 'a' + transaction * 3
        case.payload["transaction_id"] = transaction_id

    except Exception as e:
        case.message.append('transaction_id event 錯誤：' + str(e))
