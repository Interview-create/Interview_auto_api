from entity.request_entity import TestCase
from utils.tool import hash_key


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將 cash_data 中的值照 cash_key 順序 hash 替換成新的 值。

    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    try:

        if not isRequest:
            return

        hashValues = case.setting.get('cash_data', [])

        hashStr = ''
        for hashValue in hashValues:
            hashStr += str(case.payload.get(hashValue))

        key = case.setting.get('cash_key', '')
        case.payload["key"] = hash_key(hashStr, key)

    except Exception as e:
        case.message.append('cash_keep event 錯誤：' + str(e))
