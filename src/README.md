# 自動化測試 pytest Demo

本項目實現接口自動化的技術選型：Python+Requests+Pytest+Allure
，主要是針對接口項目來開展的，通過 Python+Requests 來發送和處理HTTP協議的請求接口，
使用 Pytest 作為測試執行器，使用 Json 來管理測試數據，
使用 Allure 來生成測試報告。

## 项目部署

pipenv 是 **python** 的版本管理
切到 3.9.0
開虛擬環境 automaiton
啟動虛擬環境
請先移至該專案根目錄
```shell
cd src
brew install pipenv
pipenv --python 3.9.0 install
python3 -m venv automaiton
source automaiton/bin/activate
```
## 每次打開終端后，都需要運行 source automaiton/bin/activate 命令激活虛擬環境。


pip 是 python 的套件管理 會與 pipenv 一起安裝
看一下有沒有安裝成功
```shell
pipenv --version
```

在根目錄下找到 ```requirements.txt``` 文件，然後通過 pip 工具安裝 requirements.txt 依賴，執行命令：
```shell
pipenv install -r requirements.txt
```

看有沒有安裝成功
```shell
pip3 list
```

## 目錄
### core，主要邏輯程式
### data，用來存放測試資料
### entity，資料架構，說明請看 SCHEMA.md
### tests，用來存放測試指令碼
### utils，工具

data 的部份
目錄會是, 其中 Projects 是你們放專案的目錄名稱

Projects/automation

Projects/automation-dt-data

Projects/automation-wt-data

請 CD 到 automation 根目錄後

``` bash
rm -rf src/data && echo 'success1'
ln -s ../../automation-dt-data/data/ src/ && echo 'success2'
ls -l src/data
```
會看到以下資訊

lrwxr-xr-x  1 yourname  staff  30  5 18 09:48 data -> ../../automation-dt-data/data/


## 直接執行
```shell
python3 main.py data/plan
```