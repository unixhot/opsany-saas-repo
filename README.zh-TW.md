# OpsAny 制品倉庫（repo）

[简体中文](./README.md) | [English](./README.en.md)

OpsAny 制品倉庫平台是 [OpsAny 智能維運平台](https://www.opsany.com) 的 DevOps 應用，對接 Nexus 制品倉庫，提供制品庫管理、制品上傳/下載/刪除、版本資源檢索、應用關聯等能力，幫助企業統一管理 DevOps 過程中的制品資產。

## 功能特性

- **制品庫管理**：對接 Nexus，管理制品庫（repository）的建立、刪除、查看與編輯
- **制品格式**：支援 Maven、npm、Docker、PyPI 等 Nexus 制品格式
- **制品組件 / 資源管理**：管理制品的組件與資源，支援上傳、下載、刪除
- **版本資源檢索**：按組件 / 樹結構檢索制品版本資源
- **制品搜尋**：搜尋制品組件
- **制品標籤**：為制品庫新增標籤（收藏）
- **應用關聯**：將制品庫關聯到應用平台的應用
- **複製項目**：複製程式碼倉庫到部署主機
- **制品下載**：下載制品庫制品
- **概覽統計**：制品庫數量、最近活躍、數量排名等看板

## 技術棧

- 後端：Python 3.6 + Django 2.2
- 前端：Vue 2.6
- 資料庫：MySQL + MongoDB（mongoengine）
- 容器化：Docker

## 項目結構

```bash
.
|-- blueapps                        # Python 開發框架模組
|-- blueking                        # ESB 呼叫模組
|-- component                       # 公共組件
|-- config                          # 應用設定目錄
|   |-- __init__.py                 # 應用 RUN_VER、APP_CODE 和 SECRET_KEY 等設定
|   |-- dev.py                      # 本機開發設定
|   |-- default.py                  # 全域設定
|   |-- prod.py                     # 生產環境設定
|   |-- stag.py                     # 預發布環境設定
|-- docker                          # Docker 容器化部署相關檔案
|-- frontend                        # 前端原始碼
|-- index                           # 平台入口
|-- repo                            # 制品倉庫核心業務邏輯
|-- static                          # 前端建置產物
|-- templates                       # 公共範本檔案
|-- app.yml                         # 生產打包部署設定
|-- manage.py                       # Django 工程 manage
|-- requirements.txt                # Python 依賴套件列表
|-- runtime.txt                     # Python 版本設定
|-- LICENSE                         # Apache License 2.0
```

## 依賴服務

- **OpsAny PaaS**：運行在 OpsAny PaaS 之上，依賴統一登入、ESB API 閘道等服務
- **Nexus**：制品倉庫服務，制品庫管理對接的核心服務
- **OpsAny 應用平台（devops）**：應用關聯關係依賴應用平台

## 快速開始

### 本機開發

1. 複製程式碼並安裝依賴：

```bash
pip install -r requirements.txt
```

2. 設定資料庫連線（`config/dev.py`），並初始化資料庫：

```bash
python manage.py migrate
```

3. 啟動後端服務：

```bash
python manage.py runserver 127.0.0.1:8000
```

4. 啟動前端：

```bash
cd frontend
npm install
npm run serve
```

> 更多部署與使用說明，請參考 [OpsAny 官方文檔](https://docs.opsany.com)。

## 開源協議

本項目基於 [Apache License 2.0](./LICENSE) 開源，Copyright © OpsAny.
