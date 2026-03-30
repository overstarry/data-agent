# Data Agent

基于 LangGraph 的 AI 数据查询 Agent，支持 PostgreSQL 和 Google Analytics 4 数据查询，并自动生成数据报表。

## 功能特性

- **智能查询规划**：使用 LLM 解析自然语言请求，自动生成查询计划
- **PostgreSQL 数据查询**：支持安全只读查询（仅 SELECT）
- **Google Analytics 4 集成**：调用 GA4 Data API 获取网站分析数据
- **自动报表生成**：将查询结果渲染为美观的 HTML 报表
- **状态持久化**：支持使用 PostgreSQL 作为 LangGraph checkpoint 存储

## 技术栈

- **编程语言**：Python 3.11+
- **AI Agent 框架**：LangGraph + LangChain
- **LLM**：OpenAI GPT-4o
- **数据连接**：psycopg (PostgreSQL)、google-analytics-data (GA4)
- **报表生成**：Jinja2 + Matplotlib

## 快速开始

### 1. 安装依赖

```bash
pip install -e ".[dev]"
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# PostgreSQL - 数据查询（推荐使用只读用户）
DATA_POSTGRES_URL=postgresql://readonly_user:password@localhost:5432/data_agent

# PostgreSQL - Agent 状态持久化（需要写权限）
STATE_POSTGRES_URL=postgresql://agent_user:password@localhost:5432/data_agent

# Google Analytics 4
GA_PROPERTY_ID=123456789
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# 报表输出目录
REPORT_OUTPUT_DIR=./reports
```

### 3. 运行 Agent

```bash
# 基础用法
python -m data_agent "查询最近7天的活跃用户和跳出率"

# 启用 PostgreSQL 持久化（支持断点续传）
python -m data_agent "查询最近7天的活跃用户和跳出率" --use-postgres-checkpointer

# 指定线程 ID（用于多会话管理）
python -m data_agent "查询昨日订单量" --thread-id=order-query-001
```

## Agent 工作流

```
用户请求 → Planner(LLM) → 路由决策 → 查询PG/GA → 生成报表 → 输出HTML
```

1. **Planner**：解析用户请求，生成包含 SQL 查询、GA4 指标/维度、日期范围的 JSON 计划
2. **Query Nodes**：根据计划执行 PostgreSQL 和/或 GA4 查询
3. **Report Generator**：合并结果，使用 Jinja2 模板渲染 HTML 报表

## 项目结构

```
.
├── src/data_agent/
│   ├── state.py           # AgentState 类型定义
│   ├── graph.py           # LangGraph StateGraph 组装
│   ├── edges.py           # 路由逻辑
│   ├── cli.py             # 命令行入口
│   ├── nodes/
│   │   ├── planner.py     # LLM 规划节点
│   │   ├── query_pg.py    # PostgreSQL 查询节点
│   │   ├── query_ga.py    # GA4 查询节点
│   │   └── report.py      # 报表生成节点
│   └── templates/
│       └── report.html    # HTML 报表模板
├── tests/                 # 单元测试
├── pyproject.toml         # 项目配置和依赖
└── .env.example           # 环境变量模板
```

## 运行测试

```bash
pytest
```

## 配置说明

### PostgreSQL

确保数据库用户具有只读权限（推荐）：

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public TO data_agent_user;
```

### Google Analytics 4

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 创建服务账号
2. 下载 JSON 凭证文件，设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量
3. 在 GA4 中将服务账号邮箱添加为「查看者」权限

## License

MIT
