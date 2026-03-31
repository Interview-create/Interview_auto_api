# -*- coding: utf-8 -*-
import datetime
import enum
import hmac
import json
import pytz
import sys

from typing import Tuple, Union, TypeVar
from hashlib import sha256

T = TypeVar('T')


def get_class_to_json_dumps(instance: object) -> str:
    info = {}
    for name, value in vars(instance).items():
        try:
            info[name] = value.__dict__
        except AttributeError:  # the object has no __dict__ attribute
            info[name] = value
    return json.dumps(info, ensure_ascii=False, default=str)


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    PURPLE = 4
    YELLOW = 5


def get_colored_world(color: Color, message: str):
    if color == Color.RED:
        return '\033[91m' + message + '\033[0m'
    elif color == Color.GREEN:
        return '\033[92m' + message + '\033[0m'
    elif color == Color.BLUE:
        return '\033[94m' + message + '\033[0m'
    elif color == Color.PURPLE:
        return '\033[95m' + message + '\033[0m'
    elif color == Color.YELLOW:
        return '\033[93m' + message + '\033[0m'
    else:
        return message


def split_last_slash(s: str) -> Tuple[str, str]:
    """
    將字符串 s 以最後一個 / 為界，分割成兩部分。
    :param s: 要分割的字符串
    :return: 分割後的字符串元組
    """
    index = s.rindex('/')
    return s[:index], s[index + 1:]


def hash_key(data: str, key: str):
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    h = hmac.new(key, message, digestmod=sha256)
    return h.hexdigest()


def check_type(
        data: dict,
        key: str,
        type_: Union[type, tuple[type]],
        default: T = None,
        msg: str = '',
        checkKeyExist: bool = False) -> T:
    """
    從給定的字典中檢查 key 是否存在且其值為指定的型別，若存在則回傳對應的值，否則回傳 None。
    參數：
        data (dict)：包含鍵值對的字典。
        key (str)：欲檢查的鍵。
        type_ (type 或 tuple[type])：指定的型別或型別元組。
        default (T)：如果鍵不存在於字典中，則回傳預設值。
        msg (str)：錯誤訊息的前綴。
        checkKeyExist (bool)：是否檢查鍵的存在。

    回傳：
        型別為 T 的值，或 None。

    異常：
        KeyError：如果鍵不存在於字典中且 `checkKeyExist` 為 True，則引發 KeyError。
        KeyError：如果型別不一樣，則引發 TypeError。

    範例：
        check_type({'a': 'b', 'c': 123}, 'a', str) -> 'b'
        check_type({'a': 'b', 'c': 123}, 'b', str) -> None
        check_type({'a': 'b', 'c': 123}, 'c', (str, int)) -> 123
        check_type({'a': 'b', 'c': 123}, 'd', (str, int)) -> None
    """
    if data is None:
        print(f"❌❌❌❌ {msg} 路徑或名稱錯誤，請檢查task、case路徑及名稱❌❌❌❌")
        sys.exit()

    if checkKeyExist and key not in data:
        raise KeyError(f"{msg} Key '{key}' 不存在.")
    elif not checkKeyExist and key not in data:
        return default

    value = data[key]
    if not isinstance(value, type_):
        type_names = ' or '.join(t.__name__ for t in type_) if isinstance(type_, tuple) else type_.__name__
        raise KeyError(f"{msg} '{key}' 類型必需是 {type_names}, 而不是 {type(value).__name__}")

    return value


def get_cst_time():
    cst_tz = pytz.timezone('Asia/Taipei')
    # 把當前時間轉換成 CST 時區的時間
    cstTime = datetime.datetime.now().astimezone(cst_tz)
    return cstTime
