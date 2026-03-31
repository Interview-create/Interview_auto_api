from entity.request_entity import TestCase
from utils.replace_placeholder import replace_placeholder


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 {{XX}} 替換成新的 值。
    參數:
        case (TestCase): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    try:

        if isRequest:
            # 替換 request 的值
            case.payload = replace_placeholder(case.payload, case.uuid)

            # 替換 headers 的值
            case.http.headers = replace_placeholder(case.http.headers, case.uuid)

            # 替換 url 的值
            url = {'url': case.http.url}
            url = replace_placeholder(url, case.uuid)
            case.http.url = url['url']

            return

        # 替換 response 的值
        case.expected.response = replace_placeholder(case.expected.response, case.uuid)

    except Exception as e:
        case.message.append('merge_values event 錯誤：' + str(e))
