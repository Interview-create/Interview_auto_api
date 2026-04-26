# Call Graph

每個 function 列出功能說明與被哪些 function 呼叫。

---

## main.py

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `test_main()` | CLI 入口，讀取命令列參數與環境變數，建立 `TestPlanTool` 並啟動測試 | `asyncio.run()`（腳本啟動時） |

---

## app.py

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `home()` | 列出 log 目錄下的檔案與資料夾超連結 | Flask route `GET /` |
| `serve_file(filename)` | 回傳指定 log 檔案內容 | Flask route `GET /file/<path>` |
| `serve_folder(folderName)` | 列出指定子目錄的檔案超連結 | Flask route `GET /folder/<path>` |
| `run()` | 接收 `name` 參數，透過 Celery 非同步觸發測試 | Flask route `GET /run` |
| `run_test_plan_in_background(testPlanTool, name)` | 在獨立執行緒中執行測試計畫（備用，目前以 Celery 取代） | （保留，原由 `run()` 以 gevent 呼叫） |
| `bash()` | 回傳瀏覽器終端機 HTML 頁面（WebSocket 控制） | Flask route `GET /bash` |
| `handle_run_command(data)` | 接收前端指令，執行 shell 並透過 WebSocket 回傳結果 | SocketIO event `run_command` |

---

## tasks.py

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `run_test_plan_summary_list(testPlanTool, name)` | Celery 非同步任務，包裝 `TestPlanTool.run_test_plan_summary_list()` | `app.py:run()` 呼叫 `.delay()` |

---

## core/TestPlanTool.py — `TestPlanTool`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__()` | 初始化報告路徑、時間戳、統計結構、HTML 樣板 | `main.py:test_main()`、`app.py:run()` |
| `setup()` | 非同步初始化：呼叫 `Version.get_version_html()` 取得各服務版本 HTML | `run_test_plan_summary_list()` |
| `run_test_plan_summary(summaryName)` | 單一 plan 入口，轉呼叫 `run_test_plan_summary_list()` | 外部直接呼叫（公開 API） |
| `run_test_plan_summary_list(summaryNames)` | 多 plan 主流程：初始化、解析 queue、按序執行、存統計、建報告、發通知 | `main.py:test_main()`、`tasks.py:run_test_plan_summary_list()` |
| `run_coroutine(i)` | 在新的 event loop 中執行單一 plan（供多執行緒並行使用） | `run_test_plan_summary_list()`（`threading.Thread` 目標） |
| `build_report()` | 彙整 `reportList`，組合並寫出 HTML 報告檔案 | `run_test_plan_summary_list()`、`run_coroutine()` |
| `_find_test_dirs(root_dir)` | 遞迴找出目錄下所有含 `test*.json` 的資料夾名稱 | `run_test_plan_summary_list()` |
| `_send_notification()` | 計算執行時間與統計，發送 Slack 結果通知 | `run_test_plan_summary_list()` |
| `_get_json(path)` | 靜態方法，讀取 JSON 檔案並回傳解析結果 | `run_test_plan_summary_list()` |
| `_save_statistics()` | 將本次統計寫入 `data-HHmm.json` | `run_test_plan_summary_list()` |
| `_get_statistics()` | 讀取最近 7 天的 `data-*.json`，組成歷史趨勢資料 | `run_test_plan_summary_list()` |
| `_set_data(reportList, statistics)` | 將 `TestPlan` 回傳的報告與統計合併至總結構 | `run_test_plan_summary_list()`、`run_coroutine()` |

---

## core/TestPlan.py — `TestPlan`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__(statisticsKey)` | 初始化 logger、時間戳、reportList、統計結構 | `TestPlanTool.run_test_plan_summary_list()`、`TestPlanTool.run_coroutine()` |
| `run_test_plan(planName)` | 解析 plan JSON、依序執行所有 TestCase、計算統計、產出報告資料 | `TestPlanTool.run_test_plan_summary_list()`、`TestPlanTool.run_coroutine()` |
| `_log_info(color, message, tabNum)` | 彩色 console 輸出並寫入 logger | `run_test_plan()`、`process_log()` |
| `_run_test_cases(testPlanFile)` | 以 `asyncio.gather` 並行執行所有 TestCase，回傳結果列表 | `run_test_plan()` |
| `_update_report_data(reportData, results)` | 將每個 TestCase 的 `reportData` 合併至計畫報告字典 | `run_test_plan()` |
| `_generate_summary_report(...)` | 靜態方法，組合計畫總計資料並產出 HTML 報告片段 | `run_test_plan()` |
| `process_log(case)` | 處理單一 request 的 log：計算時間、判斷通過/失敗、組合訊息、建立 Report | 作為 callback 傳入 `ApiAutomatedTool.run_test_case()` |
| `run_case(name)` | 開發用：直接以名稱執行單一 case | 手動呼叫（開發/除錯） |
| `run_task(path, name)` | 開發用：直接以路徑與名稱執行單一 task | 手動呼叫（開發/除錯） |

---

## core/TestPlanSummaryJson.py — `TestPlanSummaryJson`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__(name)` | 初始化：設定路徑、呼叫 `_set_json_in_memory()` 預載 JSON、讀取 `import.json` | `TestPlan.run_test_plan()`、`TestPlan.run_case()`、`TestPlan.run_task()`、`Version.get_version_html()` |
| `get_test_plan_summary()` | 找出目錄下所有 `test*.json`，組成 `TestPlanSummary` 物件（含總筆數） | `TestPlan.run_test_plan()` |
| `get_test_plan_file(plan)` | 解析單一 `test*.json` 檔案，組成 `TestPlanFile` 物件 | `get_test_plan_summary()` |
| `get_test_plan(name, data, count)` | 解析計畫區塊的 `cases`，支援 `loop` 與 `for_loop_key`，回傳 `TestPlan` 物件 | `get_test_plan_file()`、`Version.get_version_html()` |
| `get_case(name, count, planName)` | 從 `case.json` 取得指定案例，解析其 `tasks`，回傳 `Case` 物件 | `get_test_plan()`、`TestPlan.run_case()` |
| `get_task(path, name, count, planName)` | 從 `task.json` 組裝完整 `TestCase`，包含 api、env、headers、payload、expect、events | `get_case()`、`TestPlan.run_task()` |
| `merge_dicts(dict1, dict2)` | 遞迴合併兩個字典（base task 層與 test_case 層） | `get_task()` |
| `get_import_data(testCase, pn)` | 處理 `import_key`：依 `import.json` 產生多筆參數組合的 TestCase 列表 | `get_task()` |
| `get_expected_class(expect, msg)` | 靜態方法，從 dict 建立 `ExpectedClass`（status_code、response、responseNotExist） | `get_task()` |
| `get_env(serverName)` | 靜態方法，從 `config` 取得對應服務的 host | `get_task()` |
| `get_api(path)` | 讀取 `api.json`，建立 `ApiClass` 物件 | `get_task()` |
| `_get_json(path)` | 靜態方法，從磁碟讀取 JSON 檔案 | （備用，主流程改用記憶體版本） |
| `_get_json_by_memory(path)` | 從預載的 `fileContents` 快取取得 JSON | `__init__()`、`get_case()`、`get_api()` |
| `_get_task_json_by_memory(path, pn)` | 從快取搜尋含有指定 test_case 名稱的 task.json | `get_task()` |
| `_get_plan_files(folder_path)` | 遍歷目錄，收集所有 `test*.json` 的名稱、路徑、內容 | `get_test_plan_summary()` |
| `_set_json_in_memory(directory)` | 遞迴讀取目錄下所有 `.json` 預載至記憶體（含 case.json 合併） | `__init__()` |
| `update_json_node(jsonData, jsonPath, newValue)` | 以 JSONPath 表達式定位節點並更新值 | `get_import_data()` |
| `update_value(jsonData, path, newValue)` | 靜態方法，依路徑字串逐層定位並修改 JSON 節點值 | `update_json_node()` |

---

## core/ApiAutomatedTool.py — `ApiAutomatedTool`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__(logger)` | 初始化 logger 與 config | `TestPlan._run_test_cases()`、`Version.get_version_html()` |
| `process_request(case)` | 合併預設與案例 requestEvents，執行 `run_request_event()` | `run_test_case()` |
| `process_response(case)` | 合併預設與案例 responseEvents，執行 `run_response_event()` | `run_test_case()` |
| `check_expected(case)` | 靜態方法，比對 status_code、response JSON、檔案內容是否符合預期 | `run_test_case()` |
| `run_test_case(case, count, processLog)` | 執行單一 request 的完整流程：sleep → request_event → 發請求 → response_event → 驗證 → log | `TestPlan._run_test_cases()`、`Version.get_version_html()` |

---

## core/HtmlReport.py — `HtmlReport`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__()` | 初始化 HTML 元件常數（br、色碼、table_style CSS） | `TestPlanTool.__init__()`、`TestPlanTool.build_report()`、`TestPlan._generate_summary_report()`、`Version.get_version_html()` |
| `report_total_to_html(data, showHeader)` | 將總計統計字典轉成 HTML 表格 | `TestPlanTool.build_report()` |
| `elapsed_time_to_html(startTime, endTime)` | 產生執行時間區塊 HTML | `TestPlanTool.build_report()` |
| `report_line_chart_content_to_html(statistics)` | 以 Plotly 產生近 7 天趨勢折線圖 HTML | `TestPlanTool.build_report()` |
| `report_plan_to_html(totalData, reportData)` | 將單一計畫的總計與每筆 TestCase 結果轉成 HTML 表格 | `TestPlan._generate_summary_report()` |
| `report_version_to_html(data)` | 將各服務版本號與 URL 轉成 HTML 表格 | `Version.get_version_html()` |

---

## core/Version.py — `Version`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__(logger)` | 初始化路徑與 logger | `TestPlanTool.setup()` |
| `get_version_html()` | 讀取 `version.json`，發出所有版本查詢 request，組成版本 HTML 表格 | `TestPlanTool.setup()` |
| `process_log(case)` | 靜態 log callback：直接回傳 case 不做額外處理 | 作為 callback 傳入 `ApiAutomatedTool.run_test_case()` |
| `_get_json()` | 讀取 `version.json` 並回傳解析結果 | `get_version_html()` |

---

## core/event/__init__.py

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `run_request_event(case, logger)` | 觸發所有 request 前置事件 | `ApiAutomatedTool.process_request()` |
| `run_response_event(case, logger)` | 觸發所有 response 後置事件 | `ApiAutomatedTool.process_response()` |
| `run_event(case, isRequest, logger)` | 依 isRequest 選取事件列表，動態載入模組並呼叫 `main()` | `run_request_event()`、`run_response_event()` |

---

## utils/rest_client.py — `RestClient`

| Function | 功能說明 | 被誰呼叫 |
|----------|----------|----------|
| `__init__(logger)` | 初始化 logger | `ApiAutomatedTool.run_test_case()` |
| `request_log(url, method, ...)` | 記錄請求 url、headers、payload 至 logger（fullLog 模式） | `request()` |
| `request(url, method, payload, **kwargs)` | 依 method（GET/POST/PUT/DELETE）發送 HTTP 請求，回傳 response | `result()` |
| `result(case)` | 從 `TestCase` 取出 http 資訊，呼叫 `request()` 並回傳 response | `ApiAutomatedTool.run_test_case()` |
