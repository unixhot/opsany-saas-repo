# OpsAny 制品仓库（repo）

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

OpsAny 制品仓库平台是 [OpsAny 智能运维平台](https://www.opsany.com) 的 DevOps 应用，对接 Nexus 制品仓库，提供制品库管理、制品上传/下载/删除、版本资源检索、应用关联等能力，帮助企业统一管理 DevOps 过程中的制品资产。

## 功能特性

- **制品库管理**：对接 Nexus，管理制品库（repository）的创建、删除、查看与编辑
- **制品格式**：支持 Maven、npm、Docker、PyPI 等 Nexus 制品格式
- **制品组件 / 资源管理**：管理制品的组件与资源，支持上传、下载、删除
- **版本资源检索**：按组件 / 树结构检索制品版本资源
- **制品搜索**：搜索制品组件
- **制品标签**：为制品库添加标签（收藏）
- **应用关联**：将制品库关联到应用平台的应用
- **克隆项目**：克隆代码仓库到部署主机
- **制品下载**：下载制品库制品
- **概览统计**：制品库数量、最近活跃、数量排名等看板

## 技术栈

- 后端：Python 3.6 + Django 2.2
- 前端：Vue 2.6
- 数据库：MySQL + MongoDB（mongoengine）
- 容器化：Docker

## 项目结构

```bash
.
|-- blueapps                        # Python 开发框架模块
|-- blueking                        # ESB 调用模块
|-- component                       # 公共组件
|-- config                          # 应用配置目录
|   |-- __init__.py                 # 应用 RUN_VER、APP_CODE 和 SECRET_KEY 等配置
|   |-- dev.py                      # 本地开发配置
|   |-- default.py                  # 全局配置
|   |-- prod.py                     # 生产环境配置
|   |-- stag.py                     # 预发布环境配置
|-- docker                          # Docker 容器化部署相关文件
|-- frontend                        # 前端源码
|-- index                           # 平台入口
|-- repo                            # 制品仓库核心业务逻辑
|-- static                          # 前端构建产物
|-- templates                       # 公共模板文件
|-- app.yml                         # 生产打包部署配置
|-- manage.py                       # Django 工程 manage
|-- requirements.txt                # Python 依赖包列表
|-- runtime.txt                     # Python 版本配置
|-- LICENSE                         # Apache License 2.0
```

## 依赖服务

- **OpsAny PaaS**：运行在 OpsAny PaaS 之上，依赖统一登录、ESB API 网关等服务
- **Nexus**：制品仓库服务，制品库管理对接的核心服务
- **OpsAny 应用平台（devops）**：应用关联关系依赖应用平台

## 快速开始

### 本地开发

1. 克隆代码并安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置数据库连接（`config/dev.py`），并初始化数据库：

```bash
python manage.py migrate
```

3. 启动后端服务：

```bash
python manage.py runserver 127.0.0.1:8000
```

4. 启动前端：

```bash
cd frontend
npm install
npm run serve
```

> 更多部署与使用说明，请参考 [OpsAny 官方文档](https://docs.opsany.com)。

## 开源协议

本项目基于 [Apache License 2.0](./LICENSE) 开源，Copyright © OpsAny.
