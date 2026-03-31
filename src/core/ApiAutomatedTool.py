import asyncio
import json

from core.event import run_request_event, run_response_event
from entity.request_entity import TestCase
from utils import tool
from utils import config, json_delta
from utils.rest_client import RestClient

"""
    這裡是處理每個 request 的地方，包含:
        sleep
        request 前的 event
        發 request
        request 後的 event
        檢查預期結果
        log
"""


class ApiAutomatedTool:
    def __init__(self, logger):
        self.logger = logger
        self.config = config

    def process_request(self, case):
        # 執行 event 以及預設的 event
        case.requestEvents = self.config.defaultRequestEvents + case.events
        run_request_event(case, self.logger)

    def process_response(self, case):
        # 執行 event 以及預設的 event
        case.responseEvents = self.config.defaultResponseEvents + case.events
        run_response_event(case, self.logger)

    # 檢查 expected 結果
    @staticmethod
    def check_expected(case: TestCase):
        """
        檢查預期的結果是否符合實際的響應

        Parameters:
        - expected (dict): 預期的結果
        - response (requests.Response): 實際的響應對象

        Returns:
        - None
        """
        response = case.response
        # 如果 statusCode 不為空則檢查
        if case.expected.statusCode is not None:
            if case.expected.statusCode != response.status_code:
                messageTemp = ''.join([f"HttpStatusCode需為:{case.expected.statusCode}，結果為:{response.status_code}"])
                case.message.append(messageTemp)
                return

        # expected.response_content
        if case.expected.responseContentPath:
            # 比較文件內容是否一致
            with open(case.expected.responseContentPath, 'rb') as f:
                if f.read() != response.content:
                    case.message.append('文件下載成功但內容不一致')

        # expected.response & expected.responseNotExist 為空即不檢查
        if not case.expected.response and not case.expected.responseNotExist:
            return

        # 獲取響應中的 JSON 格式資料
        try:
            responseJson = response.json()
        except json.decoder.JSONDecodeError:
            case.message.append('沒有response內容')
            return

        case.message.extend(json_delta.diff(case.expected.response, responseJson))
        case.message.extend(json_delta.not_exist(case.expected.responseNotExist, responseJson))

    async def run_test_case(self, case: TestCase, count: int, processLog) -> bool:
        # 發出請求, 不要因為某一個 request 噴錯後面就全部停止
        try:
            case.startTime = tool.get_cst_time()

            case.count = count

            # 睡一下 😴ZZZzzz...
            await asyncio.sleep(case.sleep)

            # 處理請求的 payload & request event
            self.process_request(case)

            if config.fullLog:
                message = f'"Start {case.planName}-{case.name}" 💋👺👹🤡💩🎃🤷🏼💃🏼 凸-_-凸 😏凸ಠ益ಠ)凸  凸-_-凸 凸(>皿<)凸 凸ಠ益ಠ)凸'
                self.logger.info(message)
                message = f'case 資訊: {tool.get_class_to_json_dumps(case)}'
                self.logger.info(message)

            restClient = RestClient(self.logger)
            case.response = restClient.result(case)

            # 處理 response event
            self.process_response(case)

            # 檢查預期的結果是否符合實際的響應
            self.check_expected(case)

            case.requestTime = case.response.elapsed.total_seconds()
            return processLog(case)

        except Exception as e:
            case.message.append('run_test_case 錯誤：' + str(e))
            return processLog(case)
