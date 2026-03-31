import html
import pandas as pd
import plotly.graph_objects as go

from entity.report import Report
from datetime import datetime

TABLE_STYLE = '''
        <style>
            body {
              background-color: grey;
            }
            table {
              border: 1px solid #1C6EA4;
              background-color: #EEEEEE;
              width: 100%;
              text-align: left;
              border-collapse: collapse;
            }
            table td, table th {
              border: 1px solid #AAAAAA;
              padding: 3px 2px;
            }
            table tbody td {
              font-size: 13px;
            }
            table tr:nth-child(even) {
              background: #D0E4F5;
            }
            table thead {
              background: #1C6EA4;
              background: -moz-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
              background: -webkit-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
              background: linear-gradient(to bottom, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
              border-bottom: 2px solid #444444;
            }
            table thead th {
              font-size: 15px;
              font-weight: bold;
              color: #FFFFFF;
              border-left: 2px solid #D0E4F5;
            }
            table thead th:first-child {
              border-left: none;
            }

            table tfoot {
              font-size: 14px;
              font-weight: bold;
              color: #FFFFFF;
              background: #D0E4F5;
              background: -moz-linear-gradient(top, #dcebf7 0%, #d4e6f6 66%, #D0E4F5 100%);
              background: -webkit-linear-gradient(top, #dcebf7 0%, #d4e6f6 66%, #D0E4F5 100%);
              background: linear-gradient(to bottom, #dcebf7 0%, #d4e6f6 66%, #D0E4F5 100%);
              border-top: 2px solid #444444;
            }
            table tfoot td {
              font-size: 14px;
            }
            table tfoot .links {
              text-align: right;
            }
            table tfoot .links a{
              display: inline-block;
              background: #1C6EA4;
              color: #FFFFFF;
              padding: 2px 8px;
              border-radius: 5px;
            }
        </style>
    '''


class HtmlReport:
    def __init__(self):
        self.br = '</br>'
        self.green = '#00b894'
        self.red = '#e74c3c'
        self.table_style = TABLE_STYLE

    def elapsed_time_to_html(self, startTime: datetime, endTime: datetime) -> str:
        """
        Args:
            startTime: 開始時間
            endTime: 結束時間
        """
        report = Report()
        elapsedTimeData = report.getElapsedTime(startTime, endTime)
        df = pd.DataFrame(elapsedTimeData)

        styled_df = df.style.applymap(self.format_font_size, size=18)
        return styled_df.hide(axis="index").to_html(classes="table table-striped table-hover table-bordered", index=False)

    def report_version_to_html(self, data: dict):
        df = pd.DataFrame(data)

        styled_df = df.style.applymap(self.format_font_size, size=18)
        return styled_df.hide(axis="index").to_html(classes="table table-striped table-hover table-bordered", index=False)

    def report_total_to_html(self, data: dict, isSum: bool = False):
        sample_data = {
            'plan name': ['範例2'],
            'total': [2],
            "passed": [1],
            "failed": [1],
            "總耗時(秒)": ['0.2366秒'],
            "開始時間": ['2020-08-08 08:00:00'],
            "結束時間": ['2020-08-08 08:00:00']
        }

        df = pd.DataFrame(data)

        if isSum:
            # 計算每個 column 的總和
            sum_row = df.sum(skipna=False)
            sum_row['plan name'] = '總計'
            sum_row['開始時間'] = data['開始時間'][0]
            sum_row['結束時間'] = data['結束時間'][-1]
            # 將總和新增一列至 DataFrame 的底部
            df = pd.concat([df, pd.DataFrame(sum_row).T], ignore_index=True)

        styled_df = df.style.applymap(self.highlight_if_gt, color=self.green, subset="passed")
        styled_df = styled_df.applymap(self.highlight_if_gt, color=self.red, subset="failed")
        styled_df = styled_df.applymap(self.format_font_size, size=30)
        styled_df.set_properties(subset=['total', 'passed', 'failed'], **{'text-align': 'right'})
        return styled_df.hide(axis="index").to_html(classes="table table-striped table-hover table-bordered", index=False)

    def report_plan_to_html(self, total: dict, data: dict):
        sample_data = {
            '進度': ['1/2', '2/2'],
            '狀態': ['PASSED', 'FAILED'],
            '測試用例': ['登入加開工-登入成功', '登入加開工-成功'],
            'status_code': ['200', '201'],
            '請求執行時間': [' 0.2668s', '0.1684s'],
            'url<br>預期結果有誤': ['',
                                    '[GET] https://a.cc/api/v1/version\nHttpStatusCode需為:201，結果為:200 <bound method Response.json of <Response [200]>> {"version":"3.0.2692"}']
        }
        if not data:
            return ''

        data['url<br>預期結果有誤'] = [html.escape(v).replace('\n', '<br>') for v in data['url<br>預期結果有誤']]
        df = pd.DataFrame(data)

        styled_df = df.style.applymap(self.format_time, subset="請求執行時間")
        styled_df = styled_df.applymap(self.highlight_failed, subset="狀態")
        styled_df.set_properties(subset=['進度', 'status_code', '請求執行時間'], **{'text-align': 'right'})

        htmlBody = self.report_total_to_html(total)

        htmlBody += styled_df.hide(axis="index").to_html(classes="blueTable", index=False)

        return htmlBody

    def report_statistics_to_html(self, data: dict):
        sample_data = {
            'Failed/date': ['06-08 08', '06-08 12', '06-08 17', '06-09 08', '06-09 12', '06-09 17', '06-10 08', '06-10 12', '06-10 17'],
            'ars-api': [2, 4, 5, 2, 7, 80, 9, 10, 0],
            "ams-api": [1, 1, 1, 1, 1, 1, 1, 1, 1],
            "ars-bank-api": [1, 1, 1, 1, 1, 1, 1, 1, 1],
            "cog-api": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        }

        df = pd.DataFrame(data)

        # 將 DataFrame 進行轉置
        df = df.transpose()

        # 重置索引
        df = df.reset_index()

        # 移動索引列至第一列
        df.columns = df.iloc[0]
        df = df[1:]

        styled_df = df.style.applymap(self.format_font_size, size=18)
        htmlBody = styled_df.hide(axis="index").to_html(classes="table table-striped table-hover table-bordered", index=False)

        return htmlBody

    @staticmethod
    def report_line_chart_content_to_html(data: dict):
        # data = {
        #     '06-28 17:00': {
        #         'ars': 0,
        #         'ams': 1
        #     },
        #     '06-29 17:00': {
        #         'ars': 0,
        #         'ams': 1
        #     }
        # }

        # x = ['06-08 08', '06-08 12', '06-08 17', '06-09 08', '06-09 12', '06-09 17', '06-10 08', '06-10 12', '06-10 17']
        # y = [3, 4, 5, 2, 7, 80, 9, 10, 0]

        x = [key for key in data.keys()]

        # 將字符串轉換為 datetime 對象
        datetime_objects = [datetime.strptime(date, '%m-%d %H:%M') for date in x]

        # 對 datetime 對象進行排序
        sorted_dates = sorted(datetime_objects)

        # 將排序後的 datetime 對象再轉換回字符串
        x = [date.strftime('%m-%d %H:%M') for date in sorted_dates]

        lineData = {k2: [] for key in x for k2 in data[key]}
        for key in x:
            for k2, v in data[key].items():
                lineData[k2].append(v)

        chatData = [go.Scatter(x=x, y=value, mode='lines+markers+text', text=value, textposition='top center', name=key)
                    for key, value in lineData.items()]

        # 創建圖表佈局
        layout = go.Layout(title='failed 數量歷史', xaxis=dict(title='時間'), yaxis=dict(title='數量'))

        # 創建折線圖和表格的圖表對象
        fig1 = go.Figure(data=chatData, layout=layout)

        htmlBody = fig1.to_html()

        return htmlBody

    # region style
    def highlight_failed(self, x):
        if x == 'FAILED':
            return f'background-color: {self.red};'
        else:
            return f'background-color: {self.green};'

    @staticmethod
    def format_time(x):
        if x.startswith(' '):
            return 'background-color: pink'
        else:
            return ''

    @staticmethod
    def format_background_color(x, color):
        return f'background-color: {color};'

    @staticmethod
    def highlight_if_gt(x, color):
        if x > 0:
            return f'background-color: {color};'
        else:
            return ''

    @staticmethod
    def format_font_size(x, size):
        return f'font-size: {size}px;'

    # 合拼表格範例
    # df = pd.DataFrame([[38.0, 2.0, 18.0, 22.0, 21, np.nan], [19, 439, 6, 452, 226, 232]],
    #                   index=pd.Index(['Tumour (Positive)', 'Non-Tumour (Negative)'], name='Actual Label:'),
    #                   columns=pd.MultiIndex.from_product([['Decision Tree', 'Regression', 'Random'], ['Tumour', 'Non-Tumour']],
    #                                                      names=['Model:', 'Predicted:']))
    #
    # htmlBody += df.to_html(index=False)

    # endregion style
