# -*- coding: utf-8 -*-
import copy
import json
import os
import uuid
from typing import Optional

from constants import constants
from entity.request_entity import TestCase, ExpectedClass
from entity.test_plan_summary_json import Case, EnvClass, ApiClass, TestPlan, TestPlanSummary, TestPlanFile
from jsonpath_ng import parse
from utils import slack_help, config
from utils.logger import logger
from utils.tool import split_last_slash, check_type
from urllib.parse import urljoin
from utils.replace_placeholder import replace_placeholder

"""
    這個工具的主要功能是組織 JSON 腳本，以便所有的 request 請求可以被執行。以下是詳細步驟：
        1 掃過 data/plan 目錄下的所有資料夾，將以 test 開頭且以 .json 結尾的檔案都納入測試計畫中，並按照資料夾名稱排序。
        2 執行第一份 .json 腳本裡的 cases。以 P1_存取款_一般存款 > test_deposit.json 為例，P1_存取款_一般存款 就是 cases 的第一個項目。
        3 cases 是一個字串陣列，按照順序執行，第一個為 "ars/admin/帳房登入_superAdmin"。
        4 接下來會去目錄 data/ars/admin 的 case.json 的 key 尋找為 "帳房登入_superAdmin"。
        5 再執行該 case.json key 裡的 tasks 內容 : "post_token/帳房登入_superAdmin"。
        6 至目錄 data/ars/admin/post_token 的 task.json 的 test_cases 內容為 "帳房登入_superAdmin" 至此為一個 request。
"""


class TestPlanSummaryJson:
    def __init__(self, name: str):
        self.pn = None
        self.name = name
        self.basePath = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        self.topDir = name.split('/')[0]
        self.fileContents = self._set_json_in_memory(
            os.path.join(self.basePath, self.topDir))
        self.uuid = str(uuid.uuid4())

        # 組出 import.json 所在路徑
        planBasedirPath = os.path.join(
            self.basePath, self.topDir, "plan", "base", "import.json")
        print(f'planBasedirPath:{planBasedirPath}')

        # 讀取 import.json 檔案，並轉成 JSON 格式
        self.importJson = self._get_json_by_memory(planBasedirPath)

        self.forLoopKey: dict = {}
        self.loop: int = 1

    def get_test_plan_summary(self) -> Optional[TestPlanSummary]:
        """
        從給定的名稱中獲取測試計劃概要信息。
        參數：
            self.name (str)：測試計劃名稱。

        回傳：
            TestPlanSummary：測試計劃的概要信息。

        異常：
            Exception：如果找不到符合條件的測試案例，則引發異常。
        """
        # data/plan
        try:
            # 取得路徑下 "test" 開頭，且以 ".json" 結尾 的檔案
            planFiles = self._get_plan_files(self.name)

            testPlanFiles = []
            summaryCount = 0
            for planFile in planFiles:
                testPlanFile = self.get_test_plan_file(planFile)
                testPlanFiles.append(testPlanFile)
                summaryCount += testPlanFile.count

            testPlanSummary = TestPlanSummary(
                testPlanFiles, self.name, self.name)
            testPlanSummary.count = summaryCount
        except StopIteration:
            # 如果找不到符合條件的測試案例
            errorMessage = f"找不到與'{self.name}'相符合條件的測試案例"
            print(errorMessage)
            logger.error(errorMessage)
            return None

        return testPlanSummary

    def get_test_plan_file(self, plan: dict) -> TestPlanFile:
        """
        從給定的 dict 中獲取測試計劃檔案的詳細信息，包括包含的測試計劃和測試計劃檔案的名稱和路徑。

        參數：
            plan (dict): 包含測試計劃檔案信息的字典。

        回傳：
            TestPlanFile: 包含測試計劃檔案詳細信息的 TestPlanFile 物件。
        """
        # data/plan/範例/test_plan.json
        # 從字典中取出名稱和路徑
        name = plan['name']
        path = plan['path']

        testPlans = []
        testPlanFileCount = 0
        for key, value in plan['data'].items():
            # 獲取測試計劃
            testPlan = self.get_test_plan(key, value, testPlanFileCount)
            testPlans.append(testPlan)
            testPlanFileCount += testPlan.count

        # 建立包含測試計劃檔案詳細信息的 TestPlanFile 物件
        testPlanFile = TestPlanFile(testPlans, name=name, path=path)
        testPlanFile.fileName = name
        testPlanFile.count = testPlanFileCount
        return testPlanFile

    def get_test_plan(self, name: str, data: dict, count: int) -> TestPlan:
        """
        從給定的 dict 中獲取測試計劃檔案的詳細信息，包括包含的測試計劃和測試計劃檔案的名稱和路徑。
        參數：
            name (str)：測試計劃檔案的名稱。
            data (dict)：包含測試計劃檔案信息的字典。
            count (int)：請求數量。

        回傳：
            TestPlan：包含測試計劃的 TestPlan 物件。
        """

        # data/plan/範例/test_plan.json -> key
        # 從字典中取得 'tasks' 的值, 若找不到則回傳 空字串
        caseStrs = data.get('cases', '')

        # 執行次數，預設為1
        loop = data.get('loop', 1)

        # 基於 loop 之下的次數，若找不到則回傳 {}
        self.forLoopKey = data.get('for_loop_key', {})

        # 判斷 taskStrs 的類型是否為 list 或 tuple
        if not isinstance(caseStrs, list) or not caseStrs:
            print(f"{name}.json 的 cases 必須是個 list 且不能為空。")
            raise TypeError(f"{name}.json 的 tasks 必須是個 list 且不能為空。")

        # 建立空的 cases 清單
        cases = []
        # 設定 testPlanCount 的初始值為 0
        testPlanCount = 0
        # 將 taskStrs 轉成 list 循環 taskStrs
        for i in range(loop):
            self.loop = i
            for caseStr in caseStrs:
                # 取得 case
                case = self.get_case(caseStr, count, name)
                if case is None:
                    continue
                # 將 case 加入 cases 清單
                cases.append(copy.deepcopy(case))
                # 加 request 筆數
                count += case.count
                testPlanCount += case.count

        # 從 data 取得 description，若找不到則回傳空字串
        description = data.get('description', '')

        # 從 data 取得 tolerableSeconds，若找不到則回傳 None
        tolerableSeconds = data.get('tolerable_seconds', None)

        testPlan = TestPlan(cases, description, tolerableSeconds, name=name)
        testPlan.count = testPlanCount
        return testPlan

    def get_case(self, name: str, count: int, planName: str) -> (Case, int):
        """
        這個函式會解析測試案例檔案中的內容並創建 Case 物件。
        Case 物件封裝了測試案例中所有 task 的詳細信息，並跟踪測試案例中的筆數。
        該函式會使用 get_json 函式從 task.json 檔案中獲取詳細資訊。
        最終，函式會建立並回傳一個 Case 物件，其中包含每個 task 的詳細資訊和筆數。
        參數：
            name (str)：測試計劃檔案的名稱。
            count (int)：目前測試案例的總筆數。
            planName (str)：測試計劃檔案的名稱。

        回傳：
            Case：包含測試案例詳細資訊的 Case 物件。
            int：測試案例中的總筆數。
        """

        # data/plan/範例/test_plan.json -> key.tasks[]
        # 將 name 參數按照 '/' 分割
        path, name = split_last_slash(name)
        # 組合出 case.json 檔案的完整路徑
        jsonPath = os.path.join(self.basePath, self.topDir, path, 'case.json')
        # 讀取 json 檔案並轉成字典
        taskJson = self._get_json_by_memory(jsonPath)
        # 從 taskJson 取得 name 的資料
        if name in taskJson:
            case = taskJson[name]
        else:
            # 如果不存在 name 鍵，則進行相應的處理
            errorMessage = f"❌❌❌❌找不到與'{name}'相符合條件的測試案例，請檢查plan路徑及名稱❌❌❌❌"
            print(errorMessage)
            logger.error(errorMessage)
            return None

        # 將 name 和 path 資料新增至 case 字典中
        case['name'] = name
        case['path'] = path

        # 從 case 中取得 tasks, 若找不到則回傳空字串
        tasksStrs = case.get('tasks', '')
        # 判斷 testCaseStrs 的類型是否為 list
        if not isinstance(tasksStrs, list) or not tasksStrs:
            # 若不是則 raise TypeError 並顯示錯誤訊息
            print(f"{path}/case.json 的 tasks 必須是個 list 且不能為空。")
            raise TypeError(f"{path}/case.json 的 tasks 必須是個 list 且不能為空。")

        # 建立空的 tasks 清單
        tasks = []
        # 將 tasksStrs 轉成 list
        for taskStr in tasksStrs:
            # 因log需要顯示當前筆數
            count += 1
            # 取得 task
            task = self.get_task(path, taskStr, count, planName)

            # 將 task 加入 tasks 清單
            tasks.extend(task)

        # 使用 case 建構式建立物件
        case = Case(tasks, name=name, path=path)
        # 將 case.count 設為 tasks 的長度
        case.count = len(tasksStrs)
        return case

    def get_task(self, path: str, name: str, count: int, planName: str) -> list[TestCase]:
        """
        從指定的路徑和名稱中組合成測試任務的列表。
        參數：
            path (str)：測試計畫所在的路徑。
            name (str)：測試任務的名稱。
            count (int)：測試任務的執行次數。
            planName (str)：測試計畫的名稱。

        回傳：
            list[TestCase]：測試任務的列表。

        異常：
            Exception：如果無法找到指定的測試計畫、測試任務或任務中缺少必要的數據，則引發異常。
        """

        # 短路徑加名字, 錯誤指示用
        # path = 'ars/admin'
        # name = 'post_token/登入成功'
        pn = path + '/' + name
        self.pn = pn

        # 將 name 參數按照 '/' 分割
        # path2 = 'post_token'
        # name2 = '登入成功'
        path2, name2 = split_last_slash(name)

        # 組合出 task.json 檔案的完整路徑，且讀取 json 檔案並轉成字典
        # self.basePath = '/Users/yourName/Projects/automation/src' // 也就是你放專案的路徑
        # self.topDir = 'data_sample'
        # path = 'ars/admin'
        # path2 = 'post_token'
        # '/Users/yourName/Projects/automation/src/data_sample/ars/admin/post_token' // 全部加起來後長這樣子
        dirPath = os.path.join(self.basePath, self.topDir, path, path2)
        jsonPath = os.path.join(dirPath, 'task.json')
        # apiPath = 'ars/admin'
        apiPath = path

        # 將 name 參數按照 '/' 分割
        # path = 'post_token'
        # name = '登入成功'
        path, name = split_last_slash(name)

        # 將分割後的 path 和 apiPath 結合成完整的路徑 且 取得 api 物件
        apiPath = os.path.join(self.basePath, self.topDir, apiPath, path)
        api = self.get_api(apiPath)
        # 取得環境資料
        env = self.get_env(api.serverName)
        api.http.host = env.host
        api.http.url = api.http.url if api.http.url is not None else urljoin(
            api.http.host, api.http.path)

        # 讀取 json 檔案並轉成字典
        baseData = self._get_task_json_by_memory(dirPath, name)
        # baseData = self._get_json_by_memory(jsonPath)

        # 檢查 test_cases，且為必要的數據
        # test_case 裡每筆都為一個 request，為最小單位。
        test_cases = check_type(baseData, 'test_cases', dict, {}, pn, True)

        if name not in test_cases:
            print(f"在 {pn} task.json 中找不到名為“{name}”的測試用例")
            raise Exception(f"在 {pn} task.json 中找不到名為“{name}”的測試用例")
        value = test_cases[name]

        # 宣告 TestCase並初始化
        testCase = TestCase(name, planName)
        testCase.uuid = self.uuid
        testCase.rows = count
        testCase.serverName = api.serverName
        testCase.pathName = pn

        # 深拷貝 baseData，避免修改 baseData, task.json 上面的
        # data = copy.deepcopy(baseData) #這個太耗資源，不要用。

        data_items = [
            "files",
            "payload",
            "headers",
            "expect",
            "keep_headers_values",
            "keep_payload_values",
            "global_keep_payload_values",
            "keep_values",
            "global_keep_values",
            "setting"
        ]

        # 拷貝 baseData，避免修改 baseData, task.json 上面的
        # data = ({key: baseData.get(key, {}) for key in data_items}).copy() ＃沒有深拷貝導致headers覆蓋
        data = copy.deepcopy({key: baseData.get(key, {})
                             for key in data_items})
        data['events'] = (baseData.get('events', [])).copy()

        # 從 data 取得 payload 和 expect..，若找不到則回傳空字典和 None
        for k in data_items:
            d = check_type(data, k, dict, {}, pn)
            v = check_type(value, k, dict, {}, pn)
            # data[k] = {**d, **v} #資料很多層,用這方法無法公+私有區
            data[k] = self.merge_dicts(d, v)

        # 檢查上傳的檔案存不存在，檔名大小寫問題
        for key2, value2 in data.get('files', {}).items():
            if value2 not in os.listdir(dirPath):
                print(f"在 {pn} 需要上傳的檔案，找不到 {value2}")
                raise Exception(f"在 {pn} 需要上傳的檔案，找不到 {value2}")

        # files 資料格式組建
        testCase.files = {key: os.path.join(
            dirPath, value) for key, value in data.get('files').items()}

        # 利用 expectDict 來建立 expect 物件
        expectDict = data.get('expect')
        testCase.expected = self.get_expected_class(expectDict, pn)

        headers = data.get('headers')
        api.http.headers.update(headers)
        testCase.http = api.http

        testCase.payload = data.get('payload')
        testCase.keepHeadersValues = data.get('keep_headers_values')
        testCase.keepPayloadValues = data.get('keep_payload_values')
        testCase.globalKeepPayloadValues = data.get(
            'global_keep_payload_values')
        testCase.keepValues = data.get('keep_values')
        testCase.globalKeepValues = data.get('global_keep_values')
        testCase.setting = data.get('setting')

        # 處理 loop 要被替換的參數
        if self.forLoopKey:
            keepValuesKey = f'{constants.KEEP_VALUES_KEY}{self.uuid}'
            keepDict = json.loads(os.environ.get(keepValuesKey, '{}'))
            for key, value in self.forLoopKey.items():
                current = value.get('initial_value', 0)
                add = value.get('step_size', 1)
                prefix = value.get('prefix', '')
                fill = value.get('padding_length', 0)
                current += add * self.loop
                suffix = str(current).zfill(fill)
                keepDict[key] = prefix + suffix
                os.environ[keepValuesKey] = json.dumps(keepDict)
                testCase.payload = replace_placeholder(
                    testCase.payload, self.uuid)

        # 檔案路徑處理
        # 檔案比對
        testCase.expected.responseContentPath = None \
            if testCase.expected.responseContentPath is None else os.path.join(dirPath, testCase.expected.responseContentPath)
        # 執行 sql
        if testCase.setting and 'execute_oracle_sql' in testCase.setting:
            fileNames = check_type(
                testCase.setting, 'execute_oracle_sql', list, {}, pn)
            testCase.setting['execute_oracle_sql'] = [
                os.path.join(dirPath, sql) for sql in fileNames]

        # 從 data 取得 events 並確認是否為 list
        testCase.events = check_type(data, 'events', list, [], pn)
        testCase.events.extend(check_type(value, 'events', list, [], pn))

        # 以 test_cases 為主覆蓋掉 base，注意這會蓋掉 dict, list。
        data.update(value)

        # 從 data 取得 tolerableSeconds，若找不到則取api.tolerableSeconds，再沒有則是None
        testCase.tolerableSeconds = data.get(
            'tolerable_seconds', api.tolerableSeconds)
        testCase.sleep = data.get('sleep', 0)

        testCase.importKey = check_type(data, 'import_key', list, [], pn)
        testCase.importKey = check_type(
            value, 'import_key', list, testCase.importKey, pn)

        if not testCase.importKey:
            return [testCase]

        return self.get_import_data(testCase, pn)

    def merge_dicts(self, dict1, dict2):
        """
        递归合并两个字典，如果遇到相同键，则合并对应的值。
        """
        for key, value in dict2.items():
            if key in dict1 and isinstance(value, dict) and isinstance(dict1[key], dict):
                # 如果当前键在dict1中且对应的值都是字典，则递归合并
                dict1[key] = self.merge_dicts(dict1[key], value)
            else:
                # 否则直接赋值
                dict1[key] = value
        return dict1

    def get_import_data(self, testCase, pn):
        """
        處理 import_key 的資料

        """
        testCases = []
        # 依序讀取 testCase.importKey 中的 key，並進行檢查
        for key in testCase.importKey and self.importJson:
            # 檢查 importJson 中是否有對應的 key，且都為必填
            importInfo = check_type(self.importJson, key, dict, {}, pn, True)
            payload = check_type(importInfo, 'payload', dict, {}, pn, True)
            expect = check_type(importInfo, 'expect', dict, {}, pn, True)
            payloadKey = check_type(payload, 'key', str, '', pn, True)
            payloadValue = check_type(payload, 'value', list, [], pn, True)
            expectKey = check_type(expect, 'key', str, '', pn, True)
            expectValue = check_type(expect, 'value', list, [], pn, True)

            # 將每一個 payloadValue 和 expectValue 一一組合，並建立新的 testCase 物件
            for p, v in zip(payloadValue, expectValue):
                case = copy.deepcopy(testCase)
                case.name += f"({p}_{v})"

                self.update_json_node(case.payload, payloadKey, p)

                # 根據 expectKey 的值，修改 testCase.expected.statusCode 的值
                if expectKey == 'status_code':
                    case.expected.statusCode = v
                else:
                    self.update_json_node(case.expected, expectKey, v)

                testCases.append(case)

        return testCases

    @staticmethod
    def get_expected_class(expect: dict, msg: str) -> ExpectedClass:
        """
        從給定的字典中獲取預期的期望結果，並使用這些結果初始化 ExpectedClass 物件。
        參數：
            expect (dict)：包含期望結果的字典。

        回傳：
            ExpectedClass：使用給定的期望結果初始化的 ExpectedClass 物件。

        異常：
            Exception：如果字典中缺少必要的期望結果，則引發異常。
        """

        status = check_type(expect, 'status_code', int, 200, msg, True)
        response = expect.get('response', {})
        responseNotExist = expect.get('response_not_exist', {})
        responseContent = expect.get('response_content', None)
        return ExpectedClass(status, response, responseNotExist, responseContent)

    @staticmethod
    def get_env(serverName: str) -> EnvClass:
        """
        取得符合名稱和環境的環境物件。
        參數:
            serverName (str): 服務名稱。
            env (str): 環境代碼。

        回傳:
            EnvClass: 符合條件的環境物件。

        異常:
            ValueError: 無法找到符合條件的環境物件。
        """
        try:
            t: dict = {
                'name': serverName,
                'env': config.environment,
                'host': config.connectionSettings[serverName]['host'],
            }
            return EnvClass(t)
        except ValueError:
            print(f'env 找不到 {serverName}, 或者資料不齊。')
            raise ValueError(f'env 找不到 {serverName}, 或者資料不齊。')

    def get_api(self, path) -> ApiClass:
        """
        取得符合名稱和環境的 API 物件。
        參數:
            path (str): API 檔案所在的路徑。

        回傳:
            ApiClass: 符合條件的 API 物件。

        異常:
            ValueError: 無法找到符合條件的 API 物件。
        """

        # 將路徑與 api.json 檔案名結合成完整的檔案路徑
        jsonPath = os.path.join(path, 'api.json')

        # 讀取 json 檔案並轉成字典
        api = self._get_json_by_memory(jsonPath)

        # 使用 ApiClass 建構式建立物件並傳入字典
        return ApiClass(api)

    # region tool

    @staticmethod
    def _get_json(path: str) -> json:
        """
        讀取 json 檔案，並回傳解析後的結果
        :param path: str 檔案路徑
        :return: 解析後的結果
        """
        # 檢查檔案是否存在，若不存在則拋出錯誤
        if not os.path.exists(path):
            print(f'{path} 檔案不存在')
            raise FileNotFoundError(f'{path} 檔案不存在')
        # 讀取任務檔案
        with open(path, 'r') as jsonString:
            return json.load(jsonString)

    def _get_json_by_memory(self, path: str) -> json:
        """
        讀取 json 檔案，並回傳解析後的結果
        :param path: str 檔案路徑
        :return: 解析後的結果
        """
        # 檢查檔案是否存在，若不存在則拋出錯誤
        if path not in self.fileContents:
            print(f'{path} 檔案不存在')
            raise FileNotFoundError(f'{path} 檔案不存在')

        # 回傳任務內容
        return self.fileContents[path]

    def _get_task_json_by_memory(self, path: str, pn: str) -> json:
        """
        讀取 json 檔案，並回傳解析後的結果
        :param path: str 檔案路徑
        :return: 解析後的結果
        """
        # 讀取 dirPath 目錄下的所有檔案 task 開頭的 json 檔
        for key, value in self.fileContents.items():
            if key.startswith(path + '/task'):
                testCases = value.get('test_cases', {})
                if pn in testCases:
                    return value

    def _get_plan_files(self, folder_path):
        """
        從指定路徑中搜尋符合條件的檔案，讀取檔案內容，並回傳檔案名稱、相對路徑和內容的列表。
        參數：
            folder_path (str)：目標路徑。

        回傳：
            list：包含符合條件的檔案名稱、相對路徑和內容的列表。

        異常：
            N/A
        """
        # 獲取目標路徑的絕對路徑
        target_path = os.path.join(self.basePath, folder_path)

        file_list = []

        # 使用 os.walk() 函數遍歷資料夾
        for root, dirs, files in os.walk(target_path):
            # 依照P1、P2排序
            dirs.sort()
            for file in sorted(files):
                # 如果檔名以 "test" 開頭，且以 ".json" 結尾
                if file.startswith("test") and file.endswith(".json"):
                    # 獲取相對路徑
                    relative_path = os.path.relpath(root, self.basePath)
                    # 獲取檔案的完整路徑
                    file_path = os.path.join(root, file)
                    # 讀取檔案內容
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    # 獲取檔名不帶副檔名
                    fileName, fileExtension = os.path.splitext(file)
                    # 將檔名、檔案內容和相對路徑存儲到陣列中
                    file_list.append(
                        {"name": fileName, "path": relative_path, "data": data})

        return file_list

    @staticmethod
    def _set_json_in_memory(directory):
        fileContents = {}
        # 遍歷目錄並讀取每個文件
        for root, dirs, files in os.walk(directory):
            caseJsonContents = {}
            for filename in files:
                # 僅處理 .json 文件
                if filename.endswith(".json"):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r') as f:
                            jsonContents = json.load(f)
                            if filename.startswith("case"):
                                caseJsonContents[filepath] = jsonContents
                            else:
                                fileContents[filepath] = jsonContents
                    except Exception as e:
                        slack_help.send(
                            f"檔案{filepath} 不是完整的 json 格式 錯誤內容: {e}")
                        print(f"檔案{filepath} 不是完整的 json 格式 錯誤內容: {e}")
                        raise f"檔案{filepath} 不是完整的 json 格式 錯誤內容: {e}"

            # 處理 case 之後放回 fileContents
            if caseJsonContents:
                filepath = os.path.join(root, 'case.json')
                baseData = caseJsonContents.get(filepath)
                for key, value in caseJsonContents.items():
                    baseData.update(
                        {k: v for k, v in value.items() if k != filepath})

                fileContents[filepath] = baseData

        return fileContents

    def update_json_node(self, jsonData, jsonPath, newValue):
        """
        修改 JSON 物件中指定 JSONPath 表達式的節點值

        """
        # 定義要修改的 JSONPath 表達式
        path_to_update = parse(jsonPath)

        # 使用 jsonpath_ng 找到對應的節點
        matches = [match for match in path_to_update.find(jsonData)]

        # 修改節點的值
        if matches:
            for match in matches:
                self.update_value(jsonData, str(match.full_path), newValue)
        else:
            print(f"在 {self.pn} 需要上傳的檔案，找不到指定的 JSONPath：{jsonPath}")
            raise Exception(f"在 {self.pn} 需要上傳的檔案，找不到指定的 JSONPath：{jsonPath}")

    @staticmethod
    def update_value(jsonData, path, newValue):
        # 將 JSONPath 路徑字串拆分為路徑段落
        paths = path.split('.')

        # 取得目標節點所在的 JSON 物件
        current = jsonData

        # 迭代路徑段落，找到目標節點的父節點
        for p in paths[:-1]:
            # 判斷路徑段落是否是數字，如果是數字，則轉換為整數型態
            p = p.strip('[]')
            if p.isdigit():
                p = int(p)

            # 取得父節點
            current = current[p]

        # 取得目標節點的名稱
        last = paths[-1].strip('[]')

        # 如果目標節點名稱是數字，則轉換為整數型態
        if last.isdigit():
            last = int(last)

        # 修改目標節點的值
        current[last] = newValue

    # endregion tool
