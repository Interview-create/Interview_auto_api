# 測試資料架構

## 目錄結構


```
├── constants *常數
│   └── constants.py
├── core *測試流程主邏輯
│   ├── event *一些客製處理，例如特別的數學計算
│   │   ├── local_storage.py
│   │   ├── global_storage.py
│   │   ├── merge_expect.py
│   │   ├── merge_headers.py
│   │   └── merge_payload.py
│   ├── api_automated_tool.py *測試主要邏輯
│   ├── test_plan_json_reader.py *組合測試用例
│   └── test_plan_json_tool.py *主要是呼叫測試服務以及log組成
├── entity *抽象類別定義
│   ├── request_entity.py
│   ├── slack.py
│   └── test_plan_summary_json.py
├── utils *一些工具
│   ├── config.py
│   ├── json_delta.py
│   ├── logger.py
│   ├── replace_placeholder.py
│   ├── rest_client.py
│   ├── slack_help.py
│   └── tool.py
└── data * 測試用例存放地
    ├── plan
    │   ├── 開工
    │   │   ├── test_1_開工1.json **測試計畫集合
    │   │   └── test_2_開工2.json **測試計畫集合
    │   └── 換匯
    │       ├── test_1_換匯1.json **測試計畫集合
    │       └── test_1_換匯2.json **測試計畫集合
    ├── ars **服務名
    │   ├── admin **功能，其中每一個資料夾即是一個API
    │   │   ├── case.json **任務集合
    │   │   └── get_detail API 內容省略
    │   │   └── post_login API 主要範例
    │   │       ├── api.json **必要檔案，內有API資訊，比如路徑
    │   │       ├── 成功登入
    │   │       │   ├── task.json **必要檔案，需要做的事，比如登入
    │   │       │   ├── payload.json
    │   │       │   └── expect.json
    │   │       └── 組合參數乘積
    │   │           ├── task.json
    │   │           ├── payload.json
    │   │           └── expect.json
    │   └── proposal 功能
    │       ├── case.json
    │       └── post_user_proposal
    │           ├── api.json
    │           ├── 成功
    │           │   ├── task.json
    │           │   ├── payload.json
    │           │   └── expect.json
    │           └── 組合參數乘積
    │               ├── task.json
    │               ├── payload.json
    │               └── expect.json
    ├── ams
    └── bank
```

## 檔案內容

### env.json 環境設定

```json
{
  "environment": "dev",
  "request_verify": true,
  "env": {
    "local": {
      "ars-api": {
        "host": "",
        "host1": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "ars-bank-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "ams-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "cog-api": {
        "host": ""
      },
      "cash-mgmt-api": {
        "host": ""
      },
      "bank-mgmt-api": {
        "host": ""
      },
      "wt-ams-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      }
    },
    "dev": {
      "ars-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "ars-bank-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "ams-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "cog-api": {
        "host": ""
      },
      "cash-mgmt-api": {
        "host": ""
      },
      "bank-mgmt-api": {
        "host": ""
      },
      "wt-ams-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      }
    },
    "stage": {
      "ars-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "ars-bank-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "ams-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      },
      "cog-api": {
        "host": ""
      },
      "cash-mgmt-api": {
        "host": ""
      },
      "bank-mgmt-api": {
        "host": ""
      },
      "wt-ams-api": {
        "host": "",
        "oracle": {
          "username": "username",
          "password": "password",
          "host": "",
          "port": "1521",
          "sid": "stg"
        },
        "redis": {
          "host": "",
          "port": 6311,
          "password": "password"
        }
      }
    }
  },
  "notification_center": { // 通知
    "slack": { // slack 通知相關設定
      "webhook_url": "https://hooks.slack.com/services/a",
      "channel": "#api-auto-dev",
      "username": "Automation",
      "switch": false
    }
  },
  "default_request_events": [ // 預設事件
    "keep_values",
    "merge_values",
    "keep_values",
    "merge_values"
  ],
  "default_response_events": [ // 預設事件
    "keep_values",
    "merge_values"
  ],
  "version_path": "data/plan/base/version.json", // 版本
  "queue_path": "data/plan/base/queue.json", // 佇列
  "report_url": "http://:5001/file/", // 報告
  "full_log": true, // 是否要完整log
  "plan_name": ["data_sample/plan/範例", "data_sample/plan/範例2", "data_sample/plan/範例3", "data_sample/plan/範例4"],
  "plan_name1": ["data/plan/"] // 測試計畫路徑
}
```

### test_plan.json 測試計畫
```json  
{
  "登入加開工": { // 計畫名稱
    "environment": "dev", // 環境
    "description": "登入後開工", // 說明
    "tolerable_seconds": 1 // 預期秒數
    "測試的目的":"",
    "測試的範圍":"",
    "測試的時間":"",
    "tasks": [ // 任務 有順序性
      "ars/admin/Task_1_login", // 直接給路徑 在這個目錄必需要有 task.json
      "ars/proposal/Task_2_proposal" // Task_2_proposal 為task.json裡的 name 
    ]
  }
}

```

### task.json 任務
```json
{
  // 任務的header
  "headers": {
    "Content-Type": "text/csv",
    "Authorization": "{{ams_token}}"
  },
  // 公用 playload
  "payload": {
    "token": "{{ams_token}}",
    "agcode": null,
    "start_date": 1622502000000,
    "end_date": 1651445999000
  },
  "expect": {},
  "test_cases": {
    // 案例1
    "交收報表舊_匯出admin預設下線": {
      "description": "202305xx_DT 帳房戶口列表新增小計和總計 & 代理網交收報表、帳號總覽匯出功能",
      "payload": {
        "search_name": "admin"
      },
      // 預期結果
      "expect": {
        // 預期狀態碼
        "status_code": 200
      }
    },
    // 任務名稱 保留payload的值
    "案例2keep_payload_values": {
      "description": "取得",
      // 保留payload的值
      "keep_payload_values": {
        // abc 為payload裡的key, 值則會是1
        "ars_amount_abc": "abc",
        // def 為payload裡的key, 值則會是2
        "ars_amount_def_num": "def",
        // PLAN[0].MULTI_PROPORTION[0].PERCENT 為payload裡的key 值則會是100
        "percent_num": "PLAN[0].MULTI_PROPORTION[0].PERCENT"
      },
      "payload": {
        "abc": 1,
        "def": 2,
        "PLAN": [
          {
            "MULTI_PROPORTION": [
              {
                "PERCENT": "100"
              }
            ]
          }
        ]
      }
    },
    // 任務名稱 數字計算
    "案例3 arithmetic_operators": {
      "description": "取得",
      // 事件
      "events": [
        // 事件名稱 算術運算符
        "arithmetic_operators"
      ],
      // 設定
      "setting": {
        // 設定名, 這邊是算術運算符的keys
        "arithmetic_operators_keys": [
          // 這邊是算術運算符的key, 會找payload & expect.response
          "amounts[0].amount",
          "amounts[1].amount"
        ]
      },
      "payload": {
        "account": "{{for_loop_key1}}",
        "account2": "{{for_loop_key2}}",
        // 轉小寫 to_lower
        "account3": "to_lower({{for_loop_key2}})",
        // $guid 產生guid
        "account4": "{{$guid}}",
        // $unix_timestamp 產生unix_timestamp
        "account5": "{{$unix_timestamp}}",
        // 轉數字
        "account6": "to_num(123.123)",
        "account8": "to_num(124)"
      },
      "expect": {
        "response": {
          "version": "3.0.3¡¡3",
          "amounts": [
            {
              // 會是 100 / (1 - 2) * 100
              "amount": "{{percent_num / (1 - ars_amount_def_num) * 100}}"
            }
          ]
        }
      }
    },
    // 任務名稱 redis 命令
    "案例4 redis_command": {
      "description": "取得",
      "events": [
        // 事件名稱 redis 命令
        "redis_command"
      ],
      // 設定
      "setting": {
        // 設定名, 這邊是redis_command的內容
        "redis": {
          // 刪除
          "del": [
            // key 有支援星號
            "ARS-LMBankLoginFail-*",
            "ARS-appLongLimitRate*",
            "ARS-appMediumLimitRate*",
            "ARS-ban-*"
          ]
        }
      }
    },
    // game api 有些需要 hash payload
    "案例5 hash 指定的Key": {
      "description": "外部現金網_查詢已結算注單無資料",
      // 事件
      "events": [
        // 事件名稱 hash_keep
        "cash_keep"
      ],
      "setting": {
        // 設定名, 這邊是hash_keep的內容
        "cash_data": [
          "platform_id",
          "uuid",
          "start_time",
          "end_time",
          "page",
          "page_size"
        ],
        // 設定名, 這邊是hash_keep的內容
        "cash_key": ""
      },
      "payload": {
        "platform_id": ""
      },
      "expect": {
        "status_code": 200,
        "response": {
          "page": 1
        }
      }
    },
    // 執行 sql
    "案例6 執行 sql": {
      "description": "外部現金網_查詢已結算注單無資料",
      // 事件
      "events": [
        // 事件名稱 
        "execute_oracle_sql"
      ],
      "setting": {
        // 設定名, 這邊是execute_oracle_sql的內容
        "execute_oracle_sql": ["xxx.sql"]
      }
    }
  }
}
```

### api.json API 資訊
```json
{
  "name": "login", // API 名稱
  "description": "登入", // API 說明
  "server_name": "ars-api", // 服務名稱
  "http": {
    "method": "POST", // 方法
    "path": "api/v1/admin/token", // 路徑
    "headers": {
    }
  }
}
```

### test_case.json 測試用例
```json
{
  "case_name": "登入",
  "description": "登入成功",
  "events": [
    "is_login",
    "is_keep"
  ],
  "payload":{
    "account": "account",
    "password": "password",
    "branch": "branch",
    "form_data_uuid": "{{uuid}}"
  },
  "expect":{
    "status_code": 200,
    "response": {
      "id": 301462,
      "loginname": "account"
    }    
  }  
}
```

### payload.json 餵
```json
{
  "account": "account",
  "password": "password",
  "branch": "branch",
  "form_data_uuid": "{{uuid}}"
}
```

### expect.json 吐
```json
{
  "status_code": 200,
  "response": {
    "id": 301462,
    "loginname": "account"
  }
}
```