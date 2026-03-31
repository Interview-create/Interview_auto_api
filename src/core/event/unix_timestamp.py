from datetime import datetime
from entity.request_entity import TestCase


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 unix_timestamp 替換成新的 值,只有外部現金網登入會用到。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    try:

        if not isRequest:
            return

        if not case.payload.get("unix_timestamp", False):
            return

        case.payload["unix_timestamp"] = int(datetime.now().timestamp())

    except Exception as e:
        case.message.append('unix_timestamp event 錯誤：' + str(e))
