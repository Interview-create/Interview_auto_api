from typing import List

from entity.request_entity import Http, TestCase
from utils.logger import logger


# 定義 BaseClass 類別
class BaseClass:
    def __init__(self, name=None, path=None, jsonName=None):
        self.name = name
        self.path = path
        self.jsonName = jsonName


# 定義 api 類別
class ApiClass(BaseClass):
    def __init__(self, data, name=None, jsonName=None, path=None):
        """
        初始化 ApiClass 類別。
        參數:
            data (dict): 包含 ApiClass 類別所需資訊的字典。
            name (str, optional): 類別的名稱。
            jsonName (str, optional): 類別所對應的 JSON 檔名。
        """
        # 呼叫父類別的初始化方法
        super().__init__(name, jsonName, path)
        self.jsonName = 'api'
        self.name = data.get('name', '')
        self.path = data['path']
        self.tolerableSeconds = data.get('tolerable_seconds', None)
        self.serverName = assert_has_keys(data, 'server_name', self)
        method = assert_has_keys(data, 'method', self)
        path = assert_has_keys(data, 'path', self)
        headers = data.get('headers', {})
        url = data.get('url', None)
        self.http = Http(method, path, '', headers, url)


# 定義 env 類別
class EnvClass(BaseClass):
    def __init__(self, data: dict, name=None, jsonName=None):
        """
        初始化 EnvClass 類別。
        參數:
            data (dict): 包含 EnvClass 類別所需資訊的字典。
            classId (int, optional): 識別類別的 ID。
            name (str, optional): 類別的名稱。
            jsonName (str, optional): 類別所對應的 JSON 檔名。
        """
        # 呼叫父類別的初始化方法
        super().__init__(name, jsonName)
        self.jsonName = 'env'
        self.name = data['name']
        self.env = assert_has_keys(data, 'env', self)
        self.host = assert_has_keys(data, 'host', self)


# 定義 Task 類別
class Case(BaseClass):
    def __init__(self, testCases: list[TestCase], name=None, jsonName=None, path=None):
        """
        初始化 Task 類別。
        參數:
            testCases (list[TestCase]): 包含 TestCase 類別所需資訊的 list。
            name (str, optional): 類別的名稱。
            jsonName (str, optional): 類別所對應的 JSON 檔名。
        """
        # 呼叫父類別的初始化方法
        super().__init__(name, jsonName, path)
        self.jsonName = 'task'
        self.name = name
        self.path = path
        self.testCases = testCases
        self.count = 0


# 定義 TestPlan 類別
class TestPlan(BaseClass):
    def __init__(self,
                 tasks: list[Case],
                 description: str,
                 tolerableSeconds: int,
                 name=None,
                 jsonName=None,
                 path=None):
        """
        初始化 TestPlan 類別。
        參數:
            env (str): 環境名稱。
            tasks (list[Task]): 任務列表。
            description (str): 任務描述。
            tolerableSeconds (int): 容忍秒數。
            name (str, optional): 類別的名稱。
            jsonName (str, optional): 類別所對應的 JSON 檔名。
        """
        # 呼叫父類別的初始化方法
        super().__init__(name, jsonName, path)
        self.jsonName = 'test_plan'
        self.name = name
        self.path = path
        self.tasks = tasks
        self.description = description
        self.tolerableSeconds = tolerableSeconds
        self.count = 0


# 定義 TestPlanFile 類別
class TestPlanFile(BaseClass):
    def __init__(self,
                 testPlans: list[TestPlan],
                 name=None,
                 jsonName=None,
                 path=None):
        """
        初始化 TestPlanFile 類別。
        參數:
            testPlans (list[TestPlan]): 包含 TestPlan 類別所需資訊的 list。
            name (str, optional): 類別的名稱。
            jsonName (str, optional): 類別所對應的 JSON 檔名。
        """
        # 呼叫父類別的初始化方法
        super().__init__(name, jsonName, path)
        # 初始化 TestPlanFile 類別的屬性
        self.jsonName = 'test_plan_file'
        self.name = name
        self.path = path
        self.fileName = name
        self.testPlans = testPlans
        self.count = 0


# 定義 TestPlanSummary 類別
class TestPlanSummary(BaseClass):
    def __init__(self,
                 testPlanFiles: List[TestPlanFile],
                 name=None,
                 jsonName=None,
                 path=None):
        """
        初始化 TestPlanSummary 類別。
        參數:
            testPlanFiles (list[TestPlanFile]): 包含 TestPlanFile 類別所需資訊的 list。
            name (str, optional): 類別的名稱。
            jsonName (str, optional): 類別所對應的 JSON 檔名。
        """
        # 呼叫父類別的初始化方法
        super().__init__(name, jsonName, path)
        # 初始化 TestPlanSummary 類別的屬性
        self.jsonName = 'test_plan_summary'
        self.name = name
        self.path = path
        self.testPlanFiles = testPlanFiles
        self.count = 0


def assert_has_keys(dictionary: dict, key: str, baseClass: BaseClass):
    """
    確認字典中是否有指定的鍵

    如果鍵存在且值不為 "假值"（例如 None、0、空字符串等），則回傳值。
    否則，拋出錯誤並在日誌中記錄訊息。

    參數:
        dictionary (dict): 要檢查的字典。
        key (str): 要檢查的鍵。
        baseClass (BaseClass): 基礎類別。

    回傳:
        該鍵的值。
    """
    value = dictionary.get(key, None)
    # 檢查值是否為 "真值"（不是 None、0、空字符串等）
    if not bool(value):
        # 使用字符串格式化創建日誌消息
        log = f"{baseClass.path}/{baseClass.jsonName}.json 的name:{baseClass.name} 缺少必要{key}資訊。"
        print(log)
        logger.error(log)
        raise Exception(log)
    return value
