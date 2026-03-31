import json


def _is_container(val):
    return isinstance(val, (list, dict))


def diff(expectResponse, actualResponse, upKey: str = ''):
    """
    比對兩個json的差異
    :param expectResponse: 預期的回應
    :param actualResponse: 實際的回應
    :param upKey: 上層比對的key值
    :return: 不同之處的訊息
    """
    message = []
    if isinstance(expectResponse, dict):
        for key, value in expectResponse.items():
            if isinstance(actualResponse, dict):
                responseValue = actualResponse.get(key, 'response ¡Key 不存在')
            else:
                responseValue = actualResponse

            if _is_container(value) and _is_container(responseValue) and value:
                message.extend(
                    diff(value, responseValue, upKey=f'{upKey}{key}.'))
                continue

            value = emtpy_str_to_none(value)
            responseValue = emtpy_str_to_none(responseValue)

            checkString = check_string(value)
            if (checkString and not compare_ignore_char(responseValue, value)) or (not checkString and value != responseValue):
                message.append(f"(key:{upKey}{key} 結果需為 {type(value).__name__}({value})，".replace("\n", "\\n") +
                               f"\n實際結果為 {type(responseValue).__name__}({json.dumps(responseValue, indent=4, ensure_ascii=False)}))")

    if isinstance(expectResponse, list):
        for i, value in enumerate(expectResponse):
            if _is_container(value) and i < len(actualResponse) and _is_container(actualResponse[i]) and value:
                actual = actualResponse[i] if i < len(actualResponse) else None
                message.extend(diff(value, actual, upKey=f'{upKey}[{i}].'))
                continue

            if i > (len(actualResponse) - 1):
                message.append(f"(key:{upKey}[{i}] 結果需為 {value}，實際結果為 空)")
                return message

            value = emtpy_str_to_none(value)
            actualResponse[i] = emtpy_str_to_none(actualResponse[i])

            checkString = check_string(value)
            if (checkString and not compare_ignore_char(actualResponse[i], value)) or (not checkString and value != actualResponse[i]):
                message.append(
                    f"(key:{upKey}[{i}] 結果需為 {type(value).__name__}({value})，"
                    f"實際結果為 {type(actualResponse[i]).__name__}({json.dumps(actualResponse[i], indent=4, ensure_ascii=False)}))")

    return message


def emtpy_str_to_none(s):
    return None if s == "" or s == "None" or s == "to_num(None)" else s


def check_string(s):
    """
        Check if the given input is a string and if it contains the character '¡'.

        Parameters:
            s (any): The input to be checked.

        Returns:
            bool: True if the input is a string and contains '¡', False otherwise.
    """
    # 檢查是否為字串
    if not isinstance(s, str):
        return False
    # 檢查字串是否包含 '¡'
    if '¡' in s:
        return True
    else:
        return False


def compare_ignore_char(s1, s2, ignore_char="¡"):
    # 确保两个字符串长度相同
    if len(str(s1)) != len(s2):
        return False

    for char1, char2 in zip(str(s1), s2):
        # 如果遇到忽略字符，则跳过比较
        if char2 == ignore_char:
            continue
        # 如果字符不匹配，则返回 False
        elif char1 != char2:
            return False

    # 如果所有非忽略字符都匹配，则返回 True
    return True


def not_exist(expectResponse, actualResponse, upKey: str = ''):
    """
    檢查 expectResponse 是否不在 actualResponse 中
    :param expectResponse: 預期的回應
    :param actualResponse: 實際的回應
    :param upKey: 上層比對的 key 值
    :return: 不同之處的訊息
    只判斷 key 在不在
    "perms": {
        "1999": true,
        "2000": true,
    }
    """
    message = []
    if isinstance(expectResponse, dict):
        for key, value in expectResponse.items():
            if isinstance(actualResponse, dict):
                responseValue = actualResponse.get(key, None)
            else:
                responseValue = actualResponse

            if not _is_container(value) and responseValue is not None:
                message.append(f"(key:{upKey}{key} 不應存在)")
            elif _is_container(value) and _is_container(responseValue) and value:
                message.extend(
                    not_exist(value, responseValue, upKey=f'{upKey}{key}.'))

    return message
