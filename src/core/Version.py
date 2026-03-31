import asyncio
import json
import os

from collections import defaultdict
from core.ApiAutomatedTool import ApiAutomatedTool
from core.HtmlReport import HtmlReport
from core.TestPlanSummaryJson import TestPlanSummaryJson
from entity.request_entity import TestCase
from entity.test_plan_summary_json import TestPlan
from utils import config


class Version:
    def __init__(self, logger):
        self.logger = logger
        self.basePath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.planPath = os.path.join(self.basePath, config.versionPath)

    async def get_version_html(self):
        """
        Args:

        Returns:
            html
        """

        # 讀 json 並組成 entity
        testPlan = defaultdict(TestPlan)
        planJson = self._get_json()
        testPlanSummaryJson = TestPlanSummaryJson('data/plan/base/')
        for key, value in planJson.items():
            testPlan = testPlanSummaryJson.get_test_plan(key, value, 0)

        results = []
        # 所有物件存入 tasks 列表中，然後使用 asyncio.gather 函式等待所有物件完成
        for task in testPlan.tasks:
            apiAutomatedTool = ApiAutomatedTool(self.logger)
            tasks = [asyncio.ensure_future(apiAutomatedTool.run_test_case(case, 0, self.process_log)) for case in task.testCases]
            results.extend(await asyncio.gather(*tasks))

        data = {
            '環境': [],
            '服務名': [],
            '版本': [],
            'url': []
        }
        for item in results:
            try:
                content = item.response.content.decode('utf-8')
            except AttributeError:
                content = '取不到版號'

            data['環境'].append(config.environment)
            data['服務名'].append(item.serverName)
            data['版本'].append(content)
            data['url'].append(item.http.url)

            print(config.environment, item.serverName, content, item.http.url)

        htmlReport = HtmlReport()
        return htmlReport.report_version_to_html(data)

    @staticmethod
    def process_log(case: TestCase) -> TestCase:
        return case

    def _get_json(self) -> json:
        """
        讀取 json 檔案，並回傳解析後的結果
            :return: 解析後的結果
        """
        # 檢查檔案是否存在，若不存在則拋出錯誤
        if not os.path.exists(self.planPath):
            raise FileNotFoundError(f'{self.planPath} 檔案不存在')
        # 讀取任務檔案
        with open(self.planPath, 'r') as jsonString:
            return json.load(jsonString)
