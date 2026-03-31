import datetime
import json
import requests

from collections import defaultdict
from typing import List, Optional

from utils import tool


# 定義 ExpectedClass 類別
class ExpectedClass:
    def __init__(self, statusCode: int, response: dict, responseNotExist: dict, responseContentPath: str):
        """
        初始化 ExpectedClass 類別。
        參數:
            statusCode: HTTP 狀態碼
            response: HTTP 回應內容
            responseNotExist: HTTP 回應內容
            responseContent: HTTP 回應內容
        """
        self.statusCode = statusCode
        self.response = response
        self.responseNotExist = responseNotExist
        self.responseContentPath = responseContentPath


# 定義 Http 類別
class Http:
    """
    初始化 Http 類別。
    參數:
        method (str): HTTP 請求方法。
        path (str): HTTP 請求路徑。
        host (str): HTTP 請求網址。
        headers (str): HTTP 請求頭部資訊。
        url (str): url 網址。
    """

    def __init__(self, method: str, path: str, host: str, headers: dict, url: str):
        self.method = method
        self.path = path
        self.host = host
        self.headers = headers
        self.url = url


# 定義 TestCase 類別
class TestCase:
    """
    初始化 TestCase 類別，發request資訊，以及rcode結果。
    參數:
        name (str): 測試用例名稱。
        planName(str): 計畫名稱。
        pathName(str): 路徑名。
        serverName (str): 伺服器名稱。
        http (Http): Http 類別。
        payload (json): 伺服器傳送的資料。
        expected (ExpectedClass): 預期結果。
        rows (int): 筆數，該 request 為第幾筆。
        tolerableSeconds (int): 容忍時間。
        events (List[str]): 事件。
        keepValue (List[str]): 保留response的值。
        globalKeepValue (List[str]): 全域保留response的值。
        setting: 額外擴充用的設定資訊。
        sleep: 睡覺時間。
        importKey: 導入的key。
        startTime: 啟動時間。
        isPass: 是否通過。
        reportData: 報表資料。
        responseBody: 回應內容。
    """

    def __init__(self, name: str, planName: str):
        self.uuid: str = ''
        self.name: str = name
        self.planName: str = planName
        self.pathName: str = ''
        self.serverName: str = ''
        self.http = defaultdict(Http)
        self.files: dict = {}
        self.payload: Optional[json] = None
        self.expected = defaultdict(ExpectedClass)
        self.rows: int = 0
        self.tolerableSeconds: Optional[int] = None
        self.events: List[str] = []
        self.requestEvents: List[str] = []
        self.responseEvents: List[str] = []
        self.keepHeadersValues: dict = {}
        self.keepPayloadValues: dict = {}
        self.globalKeepPayloadValues: dict = {}
        self.keepValues: dict = {}
        self.globalKeepValues: dict = {}
        self.setting: dict = {}
        self.count: int = 0
        self.message: list[str] = []
        self.response: Optional[requests.Response] = None
        self.requestTime: int = 0
        self.sleep: int = 0
        self.importKey: list[str] = []
        self.startTime: datetime.datetime = datetime.datetime.now()
        self.isPass: bool = False
        self.reportData: dict = {}
        self.responseBody: str = '沒有 response 資訊'
