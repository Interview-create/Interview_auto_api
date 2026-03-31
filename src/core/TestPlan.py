import asyncio
import datetime
import json
import time
from typing import List

import utils
from core.ApiAutomatedTool import ApiAutomatedTool
from core.HtmlReport import HtmlReport
from core.TestPlanSummaryJson import TestPlanSummaryJson
from entity.report import Report, ReportEntity, ReportType
from entity.request_entity import TestCase
from utils import config
from utils import tool
from utils.logger import logger

"""
    執行 plan 的類別
"""


class TestPlan:
    def __init__(self, statisticsKey):
        self.tab = '    '
        self.logger = utils.logger.Logger('').logger
        self.startTime: datetime.datetime = tool.get_cst_time()
        self.reportList: list[ReportEntity] = []
        self.statisticsKey = statisticsKey
        self.statistics = {
            self.statisticsKey: {}
        }

    # 單個 plan 執行
    async def run_test_plan(self, planName: str):
        testPlanSummary = TestPlanSummaryJson(planName).get_test_plan_summary()
        self._log_info(tool.Color.YELLOW,
                       ' '.join([f'準備 執行測試總計畫: {planName}'
                                 f'此次共執行 {testPlanSummary.count}'
                                 f'個測試用例 {"*" * 20}']))

        summaryPassedCount = 0
        startTime = tool.get_cst_time()
        summaryStartRequestTime = time.perf_counter()
        reportData = {}

        # 一個 test.json 檔，可能會有多個 plan
        for testPlanFile in testPlanSummary.testPlanFiles:
            # 以該 test plan 檔名為 log 檔名 加上時間。
            if config.fullLog:
                self.logger = utils.logger.Logger(
                    testPlanFile.path.split('/')[-1]).logger

            self._log_info(tool.Color.YELLOW,
                           ' '.join([f'準備 執行測試計畫: "{testPlanFile.path}/{testPlanFile.name}",'
                                     f'此次共執行{testPlanFile.count}個測試用例']), 1)

            startRequestTime = time.perf_counter()
            results = await self._run_test_cases(testPlanFile)

            elapsedTime = time.perf_counter() - startRequestTime

            # 計算 passed 的數量
            passedCount = 0
            for case in results:
                self.statistics[self.statisticsKey].setdefault(
                    case.serverName, 0)
                # 記錄失敗的次數
                self.statistics[self.statisticsKey][case.serverName] += 0 if case.isPass else 1
                passedCount += 1 if case.isPass else 0

            summaryPassedCount += passedCount

            message = " ".join([
                f'完成 執行測試計畫: "{testPlanFile.path}/{testPlanFile.name}"',
                f'total {testPlanFile.count}, passed {passedCount}, fail {testPlanFile.count - passedCount}',
                f' 總耗時:{elapsedTime:.2f}秒',
                f' log filename :{testPlanFile.fileName}'
            ])
            self._log_info(tool.Color.BLUE, message, 1)

            self._update_report_data(reportData, results)

        endTime = tool.get_cst_time()
        summaryEndRequestTime = time.perf_counter()
        summaryElapsedTime = summaryEndRequestTime - summaryStartRequestTime

        totalData, reportHtml = self._generate_summary_report(planName, testPlanSummary, summaryPassedCount, startTime, endTime,
                                                              summaryElapsedTime, reportData)

        self.reportList.append(ReportEntity(ReportType.TOTAL, totalData))
        self.reportList.append(ReportEntity(
            ReportType.PLAN, {'reportHtml': reportHtml}))

        self._log_info(tool.Color.BLUE,
                       ' '.join([
                           f'完成 執行測試總計畫: "{planName}" total {testPlanSummary.count},'
                           f'passed {summaryPassedCount},'
                           f'fail {testPlanSummary.count - summaryPassedCount}'
                           f'總耗時:{summaryElapsedTime:.4f}秒'
                       ]))

        return self.reportList, self.statistics

    # region tool

    # 記錄資訊
    def _log_info(self, color: tool.Color, message: str, tabNum: int = 0):
        self.logger.info(message)
        coloredMessage = tool.get_colored_world(color, message)
        print(f'{self.tab * tabNum}{coloredMessage}')

    # 執行多個測試案例
    async def _run_test_cases(self, testPlanFile) -> List[TestCase]:
        results = []
        for testPlan in testPlanFile.testPlans:
            for task in testPlan.tasks:
                apiAutomatedTool = ApiAutomatedTool(self.logger)
                tasks = [asyncio.ensure_future(apiAutomatedTool.run_test_case(case, testPlanFile.count, self.process_log))
                         for case in task.testCases]
                results.extend(await asyncio.gather(*tasks))
        return results

    # 更新報告數據
    @staticmethod
    def _update_report_data(reportData, results):
        for case in results:
            for key, value in case.reportData.items():
                reportData.setdefault(key, [])
                reportData[key].append(value)

    # 生成總結報告
    @staticmethod
    def _generate_summary_report(planName, testPlanSummary, summaryPassedCount, startTime, endTime, summaryElapsedTime, reportData):
        totalData = {
            'plan name': [planName.split('/')[-1]],
            'total': [testPlanSummary.count],
            "passed": [summaryPassedCount],
            "failed": [testPlanSummary.count - summaryPassedCount],
            "總耗時(秒)": [summaryElapsedTime],
            "開始時間": [startTime.strftime("%m/%d %H:%M:%S")],
            "結束時間": [endTime.strftime("%m/%d %H:%M:%S")]
        }

        htmlReport = HtmlReport()
        reportHtml = htmlReport.report_plan_to_html(totalData, reportData)

        return totalData, reportHtml

    # 處理每個 request 的 log
    def process_log(self, case: TestCase) -> TestCase:
        """
        每個 request 的 log 處理
        """
        # 計算請求的時間
        elapsedRequestTime = case.requestTime

        # 將請求時間轉成字串並保留小數點四位
        elapsedRequestTimeStr = f'{elapsedRequestTime:.4f}'
        elapsedRequestTimeReportStr = f'{elapsedRequestTime:.4f}'

        # 是否需要判斷是否超過容許時間
        if case.tolerableSeconds is not None:
            # 判斷是否超過容許的時間，若超過則將字串轉成紫色
            elapsedRequestTimeReportStr = ' ' + elapsedRequestTimeStr \
                if elapsedRequestTime > case.tolerableSeconds else elapsedRequestTimeStr
            elapsedRequestTimeStr = tool.get_colored_world(tool.Color.PURPLE, elapsedRequestTimeStr) \
                if elapsedRequestTime > case.tolerableSeconds else elapsedRequestTimeStr

        # 取得預期訊息並用 ',' 連接
        expectedMessage = f',\n{self.tab * 6}'.join(case.message)

        # 判斷是否通過測試
        case.isPass = not bool(expectedMessage)

        # 判斷測試是否通過並決定訊息顏色
        resultWord = tool.get_colored_world(tool.Color.GREEN, 'PASSED') if case.isPass else tool.get_colored_world(tool.Color.RED,
                                                                                                                   'FAILED ')

        response = case.response
        status_code = None if response is None else getattr(
            response, 'status_code', None)

        # 若有預期結果有誤則印出錯誤訊息
        if not case.isPass:
            print(
                f"{self.tab * 3}預期結果有誤 {tool.get_colored_world(tool.Color.PURPLE, expectedMessage)}")
            self.logger.warning(expectedMessage)

        isGetResponse = not case.isPass or config.fullLog

        if isGetResponse:
            try:
                if "sms" not in response.text:
                    case.responseBody = f"\n response Json 資訊 ==> {json.dumps(response.json(), indent=4, ensure_ascii=False)}"
            except json.decoder.JSONDecodeError:
                case.responseBody = f"\n response text 資訊 ==> {response.text}"
            except Exception as e:
                case.message.append('case.responseBody 錯誤：' + str(e))

        report = Report()
        report.setPlanTest(case, status_code, elapsedRequestTimeReportStr)
        traceId = 'response.headers is None'
        if case.response and hasattr(case.response, 'headers'):
            traceId = getattr(case.response, 'headers', {}).get('trace_id', '')

        # 組合訊息
        message = ", ".join([
            resultWord,
            f'{case.rows}/{case.count}',
            f'測試用例："{case.planName}-{case.name}"',
            f'status_code：{status_code}',
            f'請求執行時間:{elapsedRequestTimeStr}秒',
            f'[{case.http.method}] [{case.serverName}] {case.http.url}',
            f'trace_id：{traceId}',
        ])

        if not case.isPass:
            message += '\n'
            message += f'request Body:{case.payload}'
            message += '\n'
            message += case.responseBody

        # 在訊息前加上 TAB
        self.logger.info(message)
        message = self.tab * 2 + message
        print(message)

        return case

    # endregion tool

    # region 開發時使用

    async def run_case(self, name: str):
        assert name, "ERROR run_case 沒有指定測試名稱"

        results = []
        testPlanSummaryJson = TestPlanSummaryJson(name)
        case = testPlanSummaryJson.get_case(name, 0, '')
        apiAutomatedTool = ApiAutomatedTool(self.logger)
        tasks = [asyncio.ensure_future(apiAutomatedTool.run_test_case(
            task, task.count, self.process_log)) for task in case.testCases]
        results.extend(await asyncio.gather(*tasks))

    async def run_task(self, path: str, name: str):
        assert name, "ERROR run_case 沒有指定測試名稱"

        testPlanSummaryJson = TestPlanSummaryJson(name)
        task = testPlanSummaryJson.get_task(path, name, 0, '')
        apiAutomatedTool = ApiAutomatedTool(self.logger)
        for t in task:
            await apiAutomatedTool.run_test_case(t, t.count, self.process_log)

    # endregion 開發時使用
