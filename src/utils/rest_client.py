import json
import requests
import urllib.parse
import urllib3

from entity.request_entity import TestCase
from utils import config

urllib3.disable_warnings()


class RestClient:
    def __init__(self, logger):
        self.logger = logger

    def request_log(self, url, method, data=None, payload=None, params=None, headers=None, files=None, cookies=None, **kwargs):
        """
        記錄 API 請求的日誌信息

        Parameters:
        - url (str): API 的請求地址
        - method (str): API 的請求方式，如 "GET"、"POST" 等
        - data (dict, optional): API 請求體中的 data 參數，默認為 None
        - payload (dict, optional): API 請求體中的 payload 參數，默認為 None
        - params (dict, optional): API 請求的 params 參數，默認為 None
        - headers (dict, optional): API 請求的頭，默認為 None
        - files (list, optional): API 請求的上傳附件列表，默認為 None
        - cookies (dict, optional): API 請求的 cookies 參數，默認為 None
        - **kwargs: 其他可選的請求參數

        Returns:
        - None: 僅記錄日誌信息，無返回值
        """
        self.logger.info("API請求方式地址: {} {}".format(method, url))
        # Python3中，json在做dumps操作時，會將中文轉換成unicode編碼，因此設置 ensure_ascii=False
        self.logger.info("API請求頭: {}".format(json.dumps(headers, indent=4, ensure_ascii=False)))
        # self.logger.info("API請求 params 參數: {}".format(json.dumps(params, indent=4, ensure_ascii=False)))
        # self.logger.info("API請求體 data 參數: {}".format(json.dumps(data, indent=4, ensure_ascii=False)))
        self.logger.info("API請求體 payload 參數: {}".format(json.dumps(payload, indent=4, ensure_ascii=False)))
        # self.logger.info("API上傳附件 files 參數: {}".format(files))
        # self.logger.info("API cookies 參數: {}".format(json.dumps(cookies, indent=4, ensure_ascii=False)))

    def request(self, url: str, method: str, payload, **kwargs):
        """
        發送 HTTP 請求

        Parameters:
        - url (str): API 的請求地址
        - method (str): API 的請求方式，如 "GET"、"POST" 等
        - payload (dict): API 請求的資料
        - **kwargs: 其他可選的請求參數

        Returns:
        - requests.Response: 發送的請求的響應對象
        """
        method = method.upper()
        # 獲取 headers、params、files 和 cookies 等可選參數
        headers = dict(**kwargs).get("headers")
        params = dict(**kwargs).get("params")
        files = dict(**kwargs).get("files")
        cookies = dict(**kwargs).get("params")
        # 記錄請求日誌
        if config.fullLog:
            self.request_log(url, method, None, payload, params, headers, files, cookies)

        session = requests.Session()

        # 發送 HTTP 請求
        if method == "GET":
            # GET 的 query string 特別處理
            query_string = []
            keys_to_delete = []

            for key, value in payload.items():
                # 如果 value 的 type 是 dict 時
                if isinstance(value, dict):
                    queryString = f'{key}={urllib.parse.quote(json.dumps(value))}'
                    query_string.append(queryString)
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del payload[key]

            query_string = "&".join(query_string)
            if query_string:
                url = f"{url}?{query_string}"
            else:
                url = f"{url}"

            response = session.get(url, params=payload, verify=config.requestVerify, timeout=config.requestTimeOut, **kwargs)
            return response
        if method == "POST":
            # POST 的 files 特別處理
            if files:
                # 處理 files 參數
                for key, value in files.items():
                    files[key] = open(value, 'rb')
                rep = session.post(url, data=payload, verify=config.requestVerify, timeout=config.requestTimeOut, **kwargs)
                # 關閉文件流
                for key in files:
                    files[key].close()
                return rep

            return session.post(url, json=payload, verify=config.requestVerify, timeout=config.requestTimeOut, **kwargs)
        if method == "PUT":
            # PUT 的 files 特別處理
            if files:
                # 處理 files 參數
                for key, value in files.items():
                    files[key] = open(value, 'rb')
                rep = session.put(url, data=payload, verify=config.requestVerify, timeout=config.requestTimeOut, **kwargs)
                # 關閉文件流
                for key in files:
                    files[key].close()
                return rep

            # PUT 和 PATCH 中没有提供直接使用json参数的方法，因此需要用data来传入
            data = json.dumps(payload)
            return session.put(url, data=data, verify=config.requestVerify, timeout=config.requestTimeOut, **kwargs)
        if method == "DELETE":
            return session.delete(url, json=payload, verify=config.requestVerify, timeout=config.requestTimeOut, **kwargs)

    def result(self, case: TestCase):
        """
        處理測試案例的結果

        Parameters:
        - name (str): 測試案例的名稱

        Returns:
        - None
        """
        # 發 request 請求
        response = self.request(url=case.http.url, method=case.http.method,
                                payload=case.payload, headers=case.http.headers, files=case.files)

        return response
