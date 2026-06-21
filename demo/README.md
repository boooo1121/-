# 单片机创意平台

基于 FastAPI + DeepSeek API 的单片机创意方案匹配与 AI 助手平台。

## 功能特性

- **创意匹配**：输入自然语言描述，自动匹配最佳方案
- **AI 助手**：基于 DeepSeek 的智能问答，专注单片机领域
- **记忆系统**：支持长期/短期记忆，持续学习
- **知识库**：Markdown 格式的元器件参数、教程、FAQ
- **10 个预设方案**：天黑自动亮灯、自动浇花、温湿度计等

## 技术栈

- **后端**：FastAPI + Python 3.8+
- **AI 模型**：DeepSeek Chat
- **前端**：静态 HTML + JavaScript
- **知识存储**：JSON + Markdown

## 项目结构

```
├── main.py              # FastAPI 入口
├── agent.py             # AI Agent 模块
├── memory.py            # 记忆管理模块
├── matcher.py           # 创意匹配模块
├── validate_keywords.py # 关键词验证
├── knowledge/           # 知识库（Markdown）
│   ├── components/      # 元器件参数
│   ├── faq/             # 常见问题
│   ├── tutorials/       # 教程文档
│   └── index.json       # 知识索引
├── data/                # 运行时数据
│   └── memory.json      # 记忆持久化存储
├── static/              # 前端静态文件
│   └── index.html       # 前端页面
├── .env                 # 环境变量（API Key）
├── .env.example         # 环境变量示例
└── .gitignore           # Git 忽略配置
```

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn pydantic
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，填入你的 DeepSeek API Key
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 启动服务

```bash
# 方式一：直接运行
python main.py

# 方式二：使用 uvicorn
uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000

## API 接口

### 创意匹配

```
POST /generate
Content-Type: application/json

{
  "text": "我想做一个自动浇花系统",
  "skip_standard": false
}
```

### AI 对话

```
POST /api/agent/chat
Content-Type: application/json

{
  "messages": [{"role": "user", "content": "ESP32 的 I2C 引脚是多少？"}],
  "temperature": 0.7
}
```

### 记忆管理

```
GET  /api/agent/memory        # 列出记忆
POST /api/agent/memory        # 添加记忆
DELETE /api/agent/memory?id=  # 删除记忆
```

## 知识库管理

### 添加新知识

1. 在 `knowledge/components/`、`knowledge/faq/` 或 `knowledge/tutorials/` 创建 Markdown 文件
2. 在文件末尾添加 `## 关键词` 部分用于搜索
3. 更新 `knowledge/index.json` 索引

### Markdown 文件格式

```markdown
# 元器件名称

## 基本信息
- 参数1: 值
- 参数2: 值

## 接线方式
| 引脚 | 功能 |
|------|------|

## MicroPython 示例
```python
# 代码
```

## 关键词
关键词1, 关键词2, 关键词3
```

## 安全提示

- API Key 存储在 `.env` 文件中，已加入 `.gitignore`
- **请勿将 `.env` 文件提交到版本控制**
- 定期轮换 API Key 保障安全

## 许可证

MIT License