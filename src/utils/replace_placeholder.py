import json
import re
import time
import uuid
import os

from constants import constants


def replace_placeholder(data: dict, keepKey: str):
    globalKeepDict = json.loads(os.environ.get(
        constants.GLOBAL_KEEP_VALUES_KEY, '{}'))
    keepDict = json.loads(os.environ.get(
        f'{constants.KEEP_VALUES_KEY}{keepKey}', '{}'))
    temp = json.dumps(data, ensure_ascii=False)

    for dictionary in [globalKeepDict, keepDict]:
        for key, value in dictionary.items():
            key_escaped = re.escape(key)
            key_end = key.split('_')[-1]

            special_keys = ["num", "json"]  # 定義一個包含特殊後綴的列表

            if key_end in special_keys:  # 檢查後綴是否在特殊列表中, 如果是, 則移除 " 符號
                if key_end == "json":
                    value = json.dumps(value)  # 將字典轉換為 json 字串
                pattern = r"\"{{" + key_escaped + "}}\""
            else:
                pattern = r"{{" + key_escaped + "}}"

            temp = re.sub(pattern, str(value), temp)

    temp = process_string(temp)
    temp = json.loads(temp)
    return temp


def process_string(s):
    # 轉大寫, 小寫 數字 文字, 預設的 guid, $unix_timestamp 替換
    patterns = {
        'to_upper': (r'to_upper\((.*?)\)', lambda x: x.group(1).upper()),
        'to_lower': (r'to_lower\((.*?)\)', lambda x: x.group(1).lower()),
        'to_num': (r'"to_num\(([-+]?\d+\.?\d*)\)"', lambda x: x.group(1)),
        'to_str': (r'to_str\((.*?)\)', lambda x: x.group(1)),
        'guid': (r'\{\{\$guid\}\}', lambda x: str(uuid.uuid4())),
        'unix_timestamp': (r'\{\{\$unix_timestamp\}\}', lambda x: str(int(time.time())))
    }

    for operation, (pattern, func) in patterns.items():
        s = re.sub(pattern, func, s)

    return s
