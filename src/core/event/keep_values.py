import datetime
import json
import os
import time

from constants import constants
from entity.request_entity import TestCase
from jsonpath_ng import parse


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    :param case:
    :param isRequest:
    Args:
        case:
        isRequest:
        **kwargs:

    Returns:

    """
    try:
        keepValuesKey = f'{constants.KEEP_VALUES_KEY}{case.uuid}'
        if isRequest:
            # 處理 keep payload, headers value
            keepDict = json.loads(os.environ.get(keepValuesKey, '{}'))
            merge_keep_value(keepDict, case.keepPayloadValues, case.payload, case, 'payload')
            merge_keep_value(keepDict, case.keepHeadersValues, case.http.headers, case, 'headers')
            for key, value in case.setting.get('time_keep_magic', {}).items():
                keepDict[key] = time_magic(value)
            for key, value in case.setting.get('time_keep_magic_ms', {}).items():
                keepDict[key] = time_magic(value) * 1000

            os.environ[keepValuesKey] = json.dumps(keepDict)

            # 處理 keep global payload value
            keepDict = json.loads(os.environ.get(constants.GLOBAL_KEEP_VALUES_KEY, '{}'))
            merge_keep_value(keepDict, case.globalKeepPayloadValues, case.payload, case, 'payload')
            os.environ[constants.GLOBAL_KEEP_VALUES_KEY] = json.dumps(keepDict)
            return

        try:
            responseJson = case.response.json()
        except json.decoder.JSONDecodeError:
            return

        # 處理 keep response value
        update_keep_values(case.keepValues, responseJson, keepValuesKey, case)

        # 處理 keep global response value
        update_keep_values(case.globalKeepValues, responseJson, constants.GLOBAL_KEEP_VALUES_KEY, case)

    except Exception as e:
        case.message.append('keep_values event 錯誤：' + str(e))


def update_keep_values(keep_values: dict, response_json, keep_key: str, case: TestCase):
    """
    Update the keep values dictionary with the response JSON and store it in the environment variable.
    使用響應 JSON 更新保留值字典並將其存儲在環境變量中。

    Parameters:
        keep_values (dict): The dictionary containing the current keep values.
        response_json: The response JSON data.
        keep_key (str): The key to access the keep values dictionary in the environment.
        case (TestCase): The current test case.

    Returns:
        None
    """
    keep_dict = json.loads(os.environ.get(keep_key, '{}'))

    if isinstance(response_json, str):
        for key, value in keep_values.items():
            keep_dict[key] = response_json
    else:
        merge_keep_value(keep_dict, keep_values, response_json, case, 'response')

    os.environ[keep_key] = json.dumps(keep_dict)


def merge_keep_value(keepDict: dict, keepValue: dict, target: dict, case: TestCase, message: str):
    """
    根據與 `target` 匹配的鍵，將 `keepValue` 中的值合併到 `keepDict` 中。

    參數：
        keepDict (dict)：要將值合併到的字典。
        keepValue (dict)：包含要合併的值的字典。
        target (dict)：要與鍵進行匹配的字典。
        case (TestCase)：TestCase 物件。
        message (str)：要附加到 case 的訊息。

    返回：
        None
    """
    for key, value in keepValue.items():
        if value is None:
            continue
        path = parse(value)
        match = path.find(target)
        if match:
            if "num" == key.split('_')[-1]:
                keepDict[key] = float(match[0].value)
            else:
                keepDict[key] = match[0].value
        else:
            case.message.append(f'{value} 不存在於 {message}')


def time_magic(time_str: str) -> int:
    """根據給定的時間字符串 time_str，返回增加指定時間後的 Unix Timestamp"""
    # 如果 time_str 不符合格式，就直接返回 Unix Timestamp
    if not time_str or not isinstance(time_str, str) or len(time_str) < 3:
        return int(time.time())

    # +9s
    # 取得正負號和時間值
    sign = time_str[0]
    value = int(time_str[1:-1])
    key = time_str[-1]

    # 計算增加指定時間後的 Unix Timestamp
    now = datetime.datetime.now()
    delta = datetime.timedelta()

    if key == 's':
        delta += datetime.timedelta(seconds=value)
    elif key == 'm':
        delta += datetime.timedelta(minutes=value)
    elif key == 'h':
        delta += datetime.timedelta(hours=value)
    elif key == 'd':
        delta += datetime.timedelta(days=value)
    elif key == 'M':
        delta += datetime.timedelta(days=30 * value)
    elif key == 'y':
        delta += datetime.timedelta(days=365 * value)

    # 如果正負號不存在，就直接返回 Unix Timestamp
    if sign == '+':
        target_time = now + delta
    elif sign == '-':
        target_time = now - delta
    else:
        return int(now.timestamp())

    return int(target_time.timestamp())
