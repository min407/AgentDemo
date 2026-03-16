# 银行智能尽调Agent系统 - 项目文档

---

## 一、需求背景

### 1.1 业务场景

在银行对公信贷业务中，客户经理需要对潜在贷款企业进行**尽职调查**（简称"尽调"）。传统流程是：

```
客户经理 → 手动收集资料 → 人工分析 → 撰写报告 → 主管审批
```

**痛点**：
- 资料收集耗时：需要登录多个系统（核心系统、天眼查、裁判文书网等）
- 人工分析效率低：一份报告平均需要2-3小时
- 报告质量参差：不同客户经理分析维度不一致
- 数据孤岛：各系统数据未打通

### 1.2 用户现状

| 角色 | 当前工作 | 痛点 |
|------|----------|------|
| 客户经理 | 手动搜集企业信息 | 耗时、重复劳动 |
| 风险经理 | 人工审核报告 | 效率低、标准不统一 |
| 审批主管 | 查看报告做决策 | 信息分散、难以横向对比 |

### 1.3 技术背景

- **模型**：银行内网使用千问或DeepSeek（可本地部署）
- **数据**：大数据平台有企业数据，但需要对接
- **网络**：部分系统需要内网访问

---

## 二、项目目标

### 2.1 核心目标

**用AI Agent自动化完成企业尽调报告，缩短报告生成时间从2小时到5分钟**

### 2.2 量化指标

| 指标 | 当前 | 目标 |
|------|------|------|
| 报告生成时间 | 2-3小时 | 5-10分钟 |
| 数据采集覆盖 | 3-4个系统 | 5+数据源 |
| 报告标准化 | 人工撰写 | 模板统一 |

### 2.3 边界约束

- 仅做**报告生成**辅助，不替代人工决策
- 数据来源：模拟 + 可扩展真实接口
- 模型：支持千问/DeepSeek（可配置）

---

## 三、用户故事

### 3.1 角色定义

| 角色 | 描述 | 权限 |
|------|------|------|
| 客户经理 | 使用系统生成尽调报告 | 查询、生成、查看 |
| 风险经理 | 审核报告、查看历史 | 查询、审核、导出 |
| 管理员 | 系统配置、数据管理 | 全部权限 |

### 3.2 用户故事

#### 故事1：快速查询
```
作为客户经理
我想输入客户名称或证件号就能查到企业信息
以便快速了解企业基本情况
```

#### 故事2：自动生成报告
```
作为客户经理
我想输入客户信息后，AI自动完成数据采集和分析
以便快速生成尽调报告
```

#### 故事3：查看分析过程
```
作为风险经理
我想看到AI的分析过程和数据来源
以便评估报告可信度
```

#### 故事4：历史记录
```
作为客户经理
我想查看之前的分析记录
以便复用历史报告
```

---

## 四、功能需求

### 4.1 核心功能

#### F1：智能查询
- 支持按客户名称查询
- 支持按统一社会信用代码查询
- 支持按客户号查询
- 自动识别输入格式

#### F2：数据采集（Agent工具）
```
数据源1：核心系统（模拟）
  - 企业基本信息
  - 账户余额
  - 交易流水摘要

数据源2：天眼查（模拟）
  - 工商信息
  - 股权结构
  - 变更记录

数据源3：舆情监控（模拟）
  - 新闻舆情
  - 司法诉讼
  - 行政处罚
```

#### F3：风险分析
```
分析维度：
1. 工商风险（经营异常、吊销等）
2. 司法风险（诉讼、被执行）
3. 舆情风险（负面新闻）
4. 经营风险（经营异常指标）
```

#### F4：报告生成
```
输出格式：
- 企业基本信息
- 风险画像（雷达图）
- 风险等级（高中低）
- 关键发现
- 建议措施
```

#### F5：历史记录
- 保存查询历史
- 支持重新生成
- 支持导出

### 4.2 流程图

```
┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 用户输入 │ -> │ 意图理解    │ -> │ 任务规划    │ -> │ 数据采集    │
│ 客户信息 │    │ (解析输入)  │    │ (拆解任务)  │    │ (多源获取)  │
└─────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              v
┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 报告展示 │ <- │ 报告生成    │ <- │ 风险分析    │ <- │ 数据汇总    │
│ (前端)   │    │ (模板填充)  │    │ (LLM分析)   │    │ (清洗合并)  │
└─────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 4.3 Agent架构

```
┌─────────────────────────────────────────────────────────┐
│                      Agent 核心                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  意图理解    │ -> │  任务规划    │ -> │  工具调用    │ │
│  │  (Intent)   │    │  (Planner)   │    │  (Tools)    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                    │     │
│                     ┌─────────────┐                │     │
│                     │  报告生成    │ <-─────────────┘     │
│                     │  (Reporter) │                      │
│                     └─────────────┘                      │
└─────────────────────────────────────────────────────────┘

工具列表：
- query_core_system   # 查询核心系统
- query_tianyancha    # 查询天眼查
- query_judgment      # 查询司法文书
- query_news          # 查询新闻舆情
```

---

## 五、非功能需求

### 5.1 性能要求

| 指标 | 要求 |
|------|------|
| 页面加载 | < 2秒 |
| 查询响应 | < 3秒 |
| 报告生成 | < 30秒 |
| 并发用户 | 支持10人 |

### 5.2 可用性

- 支持Chrome、Safari、Edge
- 响应式布局（手机+电脑）
- 错误提示友好

### 5.3 可扩展性

- 数据源模块化（可新增数据源）
- 模型可配置（千问/DeepSeek切换）
- 数据库可替换（模拟 -> MySQL）

---

## 六、技术架构

### 6.1 技术栈

```
前端：HTML5 + CSS3 + JavaScript（原生）
后端：Python Flask
AI：千问/DeepSeek（可配置）
数据：JSON模拟（可扩展SQLite/MySQL）
```

### 6.2 项目结构

```
bank_risk_agent/
├── app.py                    # Flask主程序
├── config.py                 # 配置文件
├── requirements.txt          # 依赖
│
├── agent/                    # Agent核心模块
│   ├── __init__.py
│   ├── intent.py             # 意图理解
│   ├── planner.py            # 任务规划
│   ├── collector.py          # 数据采集
│   ├── analyzer.py           # 风险分析
│   ├── reporter.py           # 报告生成
│   └── llm_client.py         # 大模型客户端
│
├── tools/                    # 工具层
│   ├── __init__.py
│   ├── core_system.py        # 核心系统模拟
│   ├── tianyancha.py         # 天眼查模拟
│   ├── judgment.py           # 司法数据模拟
│   └── news.py               # 舆情数据模拟
│
├── templates/
│   └── index.html            # 前端页面
│
└── static/
    ├── css/
    │   └── style.css         # 样式
    └── js/
        └── main.js           # 前端逻辑
```

### 6.3 部署方式

```bash
# 开发环境
python app.py
# 访问：http://localhost:5000

# 生产环境（可选）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 七、数据库设计（扩展版）

### 7.1 当前版本：模拟数据

```python
# data/mock_data.json
{
    " enterprises": {
        "A公司": {
            "credit_code": "91110000XXXXXXXX",
            "customer_no": "C2024001",
            "industry": "科技",
            "risk_level": "medium"
        }
    }
}
```

### 7.2 扩展版本：SQLite表结构

```sql
-- 客户信息表
CREATE TABLE customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    credit_code VARCHAR(18),
    customer_no VARCHAR(32),
    legal_person VARCHAR(64),
    reg_capital DECIMAL(15,2),
    establish_date DATE,
    industry VARCHAR(128),
    address TEXT,
    risk_level VARCHAR(16),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 尽调报告表
CREATE TABLE report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_no VARCHAR(32),
    customer_name VARCHAR(255),
    report_content TEXT,
    risk_summary VARCHAR(512),
    risk_level VARCHAR(16),
    data_sources VARCHAR(255),
    status VARCHAR(16) DEFAULT 'completed',
    created_by VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分析历史表
CREATE TABLE analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_no VARCHAR(32),
    customer_name VARCHAR(255),
    query_input VARCHAR(255),
    result_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 八、接口设计

### 8.1 API列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 首页 |
| POST | /api/query | 查询客户 |
| POST | /api/analyze | 开始分析 |
| GET | /api/history | 历史记录 |
| GET | /api/report/:id | 获取报告详情 |

### 8.2 接口详情

#### 8.2.1 查询客户

**请求**
```json
POST /api/query
Content-Type: application/json

{
    "keyword": "A公司"
}
```

**响应**
```json
{
    "success": true,
    "data": {
        "customer_name": "A公司",
        "credit_code": "91110000XXXXXXXX",
        "customer_no": "C2024001",
        "industry": "科技"
    }
}
```

#### 8.2.2 开始分析

**请求**
```json
POST /api/analyze
Content-Type: application/json

{
    "customer_name": "A公司",
    "credit_code": "91110000XXXXXXXX"
}
```

**响应**
```json
{
    "success": true,
    "task_id": "task_123",
    "status": "processing",
    "steps": [
        {"step": "intent", "status": "completed", "message": "意图理解完成"},
        {"step": "collect", "status": "completed", "message": "数据采集完成"},
        {"step": "analyze", "status": "completed", "message": "风险分析完成"},
        {"step": "report", "status": "completed", "message": "报告生成完成"}
    ],
    "result": {
        "risk_level": "medium",
        "summary": "企业风险可控，建议人工复核",
        "report": "..."
    }
}
```

---

## 九、前端设计

### 9.1 页面结构

```
┌─────────────────────────────────────────────────────┐
│  🏦 银行智能尽调系统                    [用户头像]  │
├────────────┬────────────────────────────────────────┤
│            │  ┌──────────────────────────────────┐  │
│  侧边栏     │  │  请输入客户名称/证件号/客户号    │  │
│            │  │  [输入框                    ][查询] │  │
│  ○ 智能查询 │  └──────────────────────────────────┘  │
│  ○ 历史记录 │                                        │
│  ○ 报告管理 │  ┌──────────────────────────────────┐  │
│  ○ 系统设置 │  │  分析进度                        │  │
│            │  │  ✓ 意图理解   ✓ 数据采集         │  │
│            │  │  ✓ 风险分析   ✓ 报告生成         │  │
│            │  └──────────────────────────────────┘  │
│            │                                        │
│            │  ┌──────────────────────────────────┐  │
│            │  │  尽调报告摘要                    │  │
│            │  │  ─────────────────────────────   │  │
│            │  │  风险等级：⚠️ 中等               │  │
│            │  │  企业名称：A公司                  │  │
│            │  │  行业：科技                      │  │
│            │  │  注册资本：1000万                 │  │
│            │  │  ...                             │  │
│            │  └──────────────────────────────────┘  │
└────────────┴────────────────────────────────────────┘
```

### 9.2 响应式布局

**电脑端 (>768px)**：侧边栏 + 主内容区

**手机端 (≤768px)**：
```
┌─────────────────┐
│ 银行智能尽调    │
├─────────────────┤
│ [输入框][查询]  │
├─────────────────┤
│ 分析进度        │
├─────────────────┤
│ 报告结果        │
├─────────────────┤
│ [底部导航]      │
└─────────────────┘
```

---

## 十、开发计划

### 10.1 任务拆分

| 序号 | 任务 | 时间 | 依赖 |
|------|------|------|------|
| 1 | 项目初始化（Flask + 目录结构） | 20min | - |
| 2 | 意图理解模块实现 | 20min | - |
| 3 | 数据采集模块实现 | 30min | - |
| 4 | 风险分析模块实现 | 30min | 3 |
| 5 | 报告生成模块实现 | 20min | 4 |
| 6 | Flask路由和API | 20min | 2-5 |
| 7 | 前端页面开发 | 30min | 6 |
| 8 | 响应式适配 | 20min | 7 |
| 9 | 联调测试 | 30min | 8 |
| 10 | 优化和演示准备 | 20min | 9 |

**总计：约4小时**

### 10.2 里程碑

- [ ] M1：后端Agent核心跑通（CLI模式）
- [ ] M2：Flask API完成
- [ ] M3：前端页面完成
- [ ] M4：联调成功
- [ ] M5：演示可用

---

## 十一、面试价值点

### 11.1 技术亮点

| 亮点 | 说明 |
|------|------|
| Agent架构 | 意图理解 -> 任务规划 -> 工具调用 -> 报告生成 |
| 模块化设计 | 各模块解耦，易扩展 |
| 响应式前端 | 手机+电脑适配 |
| 可扩展性 | 数据库、模型可配置 |

### 11.2 业务理解

| 亮点 | 说明 |
|------|------|
| 场景真实 | 银行尽调是实际业务痛点 |
| 痛点明确 | 效率低、标准化程度低 |
| 价值可量化 | 2小时 -> 5分钟 |

### 11.3 面试话术

> "我设计了一个银行智能尽调Agent系统，核心是通过Agent自动完成企业信息采集和风险分析，报告生成时间从2小时缩短到5分钟。系统采用模块化架构，支持多数据源接入..."

---

## 十二、快速开始

### 12.1 环境准备

```bash
# 1. 创建项目目录
mkdir bank_risk_agent && cd bank_risk_agent

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install flask dashscope requests
```

### 12.2 项目初始化

```
bank_risk_agent/
├── app.py                    # Flask主程序 ← 起点
├── config.py                 # 配置文件
├── requirements.txt          # 依赖
├── agent/                    # Agent核心
├── tools/                    # 工具层
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── data/
    └── mock_data.json
```

### 12.3 启动命令

```bash
# 开发模式运行
python app.py

# 浏览器访问
http://localhost:5000
```

### 12.4 测试流程

1. 打开浏览器访问 `http://localhost:5000`
2. 输入客户名称：`A公司` 或 证件号：`91110000XXXXXXXX`
3. 点击「开始分析」
4. 查看报告结果

---

## 十三、配置说明

### 13.1 环境变量（.env）

```bash
# 创建 .env 文件
FLASK_ENV=development
FLASK_DEBUG=1

# 模型配置（可选，不配则用模拟模式）
DASHSCOPE_API_KEY=sk-xxxxxxxx

# 数据库配置（扩展用）
DB_TYPE=sqlite
DB_PATH=./data/risk.db
```

### 13.2 config.py 内容

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'

    # 模型配置
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'mock')  # mock/qwen/deepseek
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')

    # 数据配置
    MOCK_DATA_PATH = './data/mock_data.json'
    DB_TYPE = os.getenv('DB_TYPE', 'mock')
    DB_PATH = os.getenv('DB_PATH', './data/risk.db')

    # 超时配置
    REQUEST_TIMEOUT = 30
    LLM_TIMEOUT = 60
```

---

## 十四、Mock数据示例

### 14.1 企业基本信息

```json
{
    "enterprises": {
        "A公司": {
            "credit_code": "91110000MA7A8XXXXX",
            "customer_no": "C20240001",
            "customer_name": "A公司",
            "legal_person": "张三",
            "reg_capital": 10000000,
            "establish_date": "2018-03-15",
            "industry": "软件开发",
            "address": "北京市海淀区中关村",
            "business_scope": "软件开发、技术咨询",
            "employees": 50,
            "risk_level": "medium"
        },
        "B科技有限公司": {
            "credit_code": "91310000MB2XXXXX",
            "customer_no": "C20240002",
            "customer_name": "B科技有限公司",
            "legal_person": "李四",
            "reg_capital": 5000000,
            "establish_date": "2020-06-20",
            "industry": "信息技术",
            "address": "上海市浦东新区",
            "business_scope": "软件开发、系统集成",
            "employees": 30,
            "risk_level": "low"
        },
        "C实业集团": {
            "credit_code": "91440000MACXXXXX",
            "customer_no": "C20240003",
            "customer_name": "C实业集团",
            "legal_person": "王五",
            "reg_capital": 500000000,
            "establish_date": "2010-01-10",
            "industry": "房地产",
            "address": "广州市天河区",
            "business_scope": "房地产开发、物业管理",
            "employees": 500,
            "risk_level": "high"
        }
    }
}
```

### 14.2 交易流水数据

```json
{
    "transactions": {
        "C20240001": {
            "period": "2024-01 to 2024-03",
            "total_inflow": 8500000,
            "total_outflow": 8200000,
            "balance": 3500000,
            "avg_monthly_income": 2800000,
            "avg_monthly_expense": 2730000,
            "large_transactions": [
                {"date": "2024-02-15", "amount": 2000000, "type": "out", "desc": "设备采购"},
                {"date": "2024-03-10", "amount": 1500000, "type": "in", "desc": "项目回款"}
            ]
        }
    }
}
```

### 14.3 司法风险数据

```json
{
    "judicial": {
        "C20240001": {
            "lawsuits": [],
            "executors": [],
            "dishonest": false,
            "risk_score": 20
        },
        "C20240003": {
            "lawsuits": [
                {"case_id": "(2024)粤01民初1234号", "type": "民事", "amount": 5000000, "status": "审理中"},
                {"case_id": "(2023)粤01民初5678号", "type": "合同纠纷", "amount": 800000, "status": "已结案"}
            ],
            "executors": [],
            "dishonest": false,
            "risk_score": 65
        }
    }
}
```

### 14.4 舆情数据

```json
{
    "sentiments": {
        "C20240001": {
            "news": [
                {"title": "A公司获得高新技术企业认定", "date": "2024-02-01", "sentiment": "positive"}
            ],
            "alerts": [],
            "risk_score": 10
        },
        "C20240003": {
            "news": [
                {"title": "C实业集团项目延期交付引业主维权", "date": "2024-03-05", "sentiment": "negative"},
                {"title": "C实业集团被曝资金链紧张", "date": "2024-02-20", "sentiment": "negative"}
            ],
            "alerts": [
                {"type": "负面舆情", "level": "high", "desc": "近期有多起负面报道"}
            ],
            "risk_score": 80
        }
    }
}
```

---

## 十五、LLM调用示例

### 15.1 意图理解 Prompt

```python
INTENT_PROMPT = """你是一个银行尽调系统的意图理解模块。

用户输入：{user_input}

请解析用户的查询意图，返回JSON格式：
{{
    "intent": "query_customer | generate_report | query_history",
    "entity_type": "customer_name | credit_code | customer_no | unknown",
    "entity_value": "实际提取的实体值",
    "confidence": 0.0-1.0之间的置信度
}}

注意：
- 如果无法识别，返回 intent="unknown"
- 只返回JSON，不要其他内容
"""
```

### 15.2 风险分析 Prompt

```python
ANALYZE_PROMPT = """你是一个银行风险分析师。请根据以下企业信息进行风险评估。

企业名称：{customer_name}
行业：{industry}
注册资本：{reg_capital}

工商信息：{business_info}
交易流水：{transaction_info}
司法风险：{judicial_info}
舆情信息：{sentiment_info}

请从以下4个维度进行分析：
1. 工商风险（经营异常、吊销等）
2. 司法风险（诉讼、被执行）
3. 舆情风险（负面新闻）
4. 经营风险（流水异常指标）

返回JSON格式：
{{
    "risk_level": "low | medium | high",
    "dimensions": {{
        "business_risk": {{"score": 0-100, "finding": "发现"}},
        "judicial_risk": {{"score": 0-100, "finding": "发现"}},
        "sentiment_risk": {{"score": 0-100, "finding": "发现"}},
        "operation_risk": {{"score": 0-100, "finding": "发现"}}
    }},
    "key_findings": ["关键发现1", "关键发现2"],
    "recommendations": ["建议1", "建议2"]
}}
"""
```

### 15.3 报告生成 Prompt

```python
REPORT_PROMPT = """你是一个银行尽调报告生成器。请根据分析结果生成专业报告。

企业名称：{customer_name}
风险等级：{risk_level}

风险分析详情：{analysis_result}

请生成一份结构化的尽调报告摘要，包含：
1. 企业基本信息
2. 风险画像（各维度得分）
3. 风险等级和结论
4. 关键发现
5. 建议措施

报告要简洁专业，适合银行审批人员阅读。
"""
```

---

## 十六、错误处理

### 16.1 异常类型

| 异常类型 | 原因 | 处理方式 |
|----------|------|----------|
| EntityNotFoundException | 客户不存在 | 返回友好提示 |
| DataSourceException | 数据源调用失败 | 降级处理，返回部分数据 |
| LLMException | 大模型调用失败 | 使用规则引擎兜底 |
| TimeoutException | 请求超时 | 重试或返回超时提示 |

### 16.2 错误响应格式

```json
{
    "success": false,
    "error": {
        "code": "ENTITY_NOT_FOUND",
        "message": "未找到该客户信息",
        "detail": "请检查客户名称或证件号是否正确"
    }
}
```

### 16.3 代码示例

```python
class AgentException(Exception):
    """Agent基础异常"""
    def __init__(self, code, message, detail=None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(self.message)

class EntityNotFoundException(AgentException):
    def __init__(self, entity):
        super().__init__(
            "ENTITY_NOT_FOUND",
            f"未找到客户: {entity}",
            "请检查客户名称或证件号是否正确"
        )

# 在Flask中使用
@app.errorhandler(AgentException)
def handle_agent_exception(e):
    return jsonify({
        "success": False,
        "error": {
            "code": e.code,
            "message": e.message,
            "detail": e.detail
        }
    }), 400
```

---

## 十七、日志说明

### 17.1 日志级别

| 级别 | 用途 | 触发场景 |
|------|------|----------|
| DEBUG | 调试信息 | 开发时查看详情 |
| INFO | 正常流程 | 查询、分析、报告生成 |
| WARNING | 警告 | 数据不完整、降级处理 |
| ERROR | 错误 | 异常情况 |

### 17.2 日志格式

```
2024-03-16 10:30:15 [INFO] agent.intent: 意图理解开始 - 输入: A公司
2024-03-16 10:30:15 [INFO] agent.collector: 调用工具 query_core_system
2024-03-16 10:30:16 [INFO] agent.collector: 数据采集完成 - 来源: 3个
2024-03-16 10:30:16 [INFO] agent.analyzer: 风险分析完成 - 风险等级: medium
2024-03-16 10:30:17 [INFO] agent.reporter: 报告生成完成
2024-03-16 10:30:17 [INFO] api.analyze: 请求完成 - 耗时: 2.3s
```

### 17.3 配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('./logs/agent.log'),
        logging.StreamHandler()
    ]
)
```

---

## 十八、安全考虑

### 18.1 当前版本（开发演示）

- 无认证（演示用）
- 数据存储在内存/JSON文件

### 18.2 生产环境建议

| 安全项 | 建议 |
|--------|------|
| 认证 | 添加JWT/Session认证 |
| 权限 | 角色分级（客户经理/风险经理/管理员） |
| 审计 | 记录所有操作日志 |
| 脱敏 | 敏感信息脱敏处理 |
| 网络 | 内网部署，HTTPS |
| API | 限流防刷 |

---

## 十九、部署指南（面试展示用）

### 19.1 本地开发模式

```bash
# 1. 进入项目目录
cd bank_risk_agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python app.py

# 4. 访问
http://localhost:5000
```

### 19.2 GitHub + Vercel 部署（推荐）

这是最标准的展示方式：代码放GitHub，演示用Vercel

**第一步：推送到GitHub**

```bash
# 1. 初始化Git（如果还没）
cd bank_risk_agent
git init

# 2. 创建GitHub仓库（手动在GitHub网站创建）
# 假设仓库名：bank-risk-agent

# 3. 关联远程仓库
git remote add origin https://github.com/你的用户名/bank-risk-agent.git

# 4. 添加文件（排除不需要的）
echo "venv/
__pycache__/
*.pyc
.env
*.log" > .gitignore

# 5. 提交
git add .
git commit -m "feat: 银行智能尽调Agent系统 v1.0"

# 6. 推送到GitHub
git branch -M main
git push -u origin main
```

**第二步：Vercel部署**

```bash
# 方式A：CLI部署
vercel --prod

# 方式B：GitHub自动部署（推荐）
# 1. 登录 vercel.com
# 2. Import GitHub仓库
# 3. 自动部署，无需配置
```

**最终效果**：
```
GitHub源码：https://github.com/你的用户名/bank-risk-agent
在线演示：  https://bank-risk-agent.vercel.app
```

**面试展示时**：
> "这是项目的GitHub地址，大家可以看源码。这是演示链接，可以直接体验..."

---

### 19.3 目录结构（Git推送用）

```
bank_risk_agent/
├── .gitignore           # 忽略 venv/__pycache__ 等
├── requirements.txt     # Python依赖
├── vercel.json          # Vercel配置
├── app.py               # 主程序
├── config.py            # 配置文件
├── agent/               # Agent核心
├── tools/               # 工具层
├── templates/           # HTML模板
├── static/              # 静态资源
├── data/                # 模拟数据
└── docs/                # 文档（可选是否推送）
```

### 19.3 面试展示方式

| 场景 | 展示方式 |
|------|----------|
| 线上面试 | 发Vercel链接给面试官点击 |
| 线下面试 | 笔记本浏览器直接演示 |
| 录屏演示 | 录2分钟操作视频备用 |

---

## 二十、验收标准

### 20.1 功能验收

- [ ] 能通过客户名称查询到企业信息
- [ ] 能触发完整的Agent分析流程
- [ ] 能展示4个步骤的状态
- [ ] 能显示风险等级和报告摘要
- [ ] 响应式布局手机电脑都能用

### 20.2 性能验收

- [ ] 页面加载 < 2秒
- [ ] 报告生成 < 10秒（模拟模式）
- [ ] 无明显JS错误

### 20.3 部署验收

- [ ] Vercel部署成功
- [ ] 外部网络可访问
- [ ] URL可正常打开页面

---

## 二十一、下一步

确认文档后，我将：
1. 画出前端原型图（使用Pencil）
2. 开始代码实现

---

**文档版本**：V1.2
**最后更新**：2024-03-16
