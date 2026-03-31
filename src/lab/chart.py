import os
import pandas as pd
import plotly.graph_objects as go

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

# 創建數據
x = ['06-08 08', '06-08 12', '06-08 17', '06-09 08', '06-09 12', '06-09 17', '06-10 08', '06-10 12', '06-10 17']
y = [3, 4, 5, 2, 7, 80, 9, 10, 0]
# labels = [str(num) for num in y]  # 將數字轉換為字符串

# 創建折線圖的數據點
trace = go.Scatter(x=x, y=y, mode='lines+markers+text', text=y, textposition="top center")

# 創建圖表佈局
layout = go.Layout(title='', xaxis=dict(title=''), yaxis=dict(title='數量'))

# 創建表格數據
data = {
    'Failed\date': ['06-08 08', '06-08 12', '06-08 17', '06-09 08', '06-09 12', '06-09 17', '06-10 08', '06-10 12', '06-10 17'],
    'ars-api': [2, 4, 5, 2, 7, 80, 9, 10, 0],
    "ams-api": [1, 1, 1, 1, 1, 1, 1, 1, 1],
    "ars-bank-api": [1, 1, 1, 1, 1, 1, 1, 1, 1],
    "cog-api": [1, 1, 1, 1, 1, 1, 1, 1, 1]
}
df = pd.DataFrame(data)

# 轉換 DataFrame 為與表格相同的資料格式
table_data = df.to_dict(orient='list')

# 將 DataFrame 進行轉置
df = df.transpose()

# 重置索引
df = df.reset_index()

# 移動索引列至第一列
df.columns = df.iloc[0]
df = df[1:]


def format_font_size(x, size):
    return f'font-size: {size}px;'


styled_df = df.style.applymap(format_font_size, size=18)
tableContent = styled_df.hide(axis="index").to_html(classes="table table-striped table-hover table-bordered", index=False)

# 創建折線圖和表格的圖表對象
fig1 = go.Figure(data=[trace], layout=layout)

# 將圖表保存為 HTML 文件
basePath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
chartPath = f'{basePath}/line_chart.html'
tablePath = f'{basePath}/table.html'

lineChartContent = fig1.to_html()

# 讀取 line_chart.html 的內容
# basePath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# lineChartPath = f'{basePath}/line_chart.html'
# with open(lineChartPath, 'r') as lineChartFile:
#     lineChartContent = lineChartFile.read()

# 生成 combined_chart.html 的內容
combinedContent = f'''
<html>
<head>
    <title>Combined Chart</title>
</head>
{TABLE_STYLE}
<body>
    {lineChartContent}
    {tableContent}
    </br>
    </br>
    </br>
</body>
</html>
'''

# 將 combined_chart.html 的內容保存為文件
combinedPath = f'{basePath}/combined_chart.html'
with open(combinedPath, 'w') as combinedFile:
    combinedFile.write(combinedContent)
