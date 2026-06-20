# 单片机创意平台 V0.1 Demo

零基础用户打开网页、输入创意、一键完成 ESP32-S3 固件烧录与程序部署。

## 快速开始

```bash
# 1. 安装依赖
pip install fastapi uvicorn

# 2. 启动服务
python main.py

# 3. 打开浏览器访问
# http://localhost:8000
```

## 项目结构

```
demo/
├── main.py                  # FastAPI 路由
├── matcher.py               # 匹配引擎
├── validate_keywords.py     # 触发词校验脚本
├── data/
│   ├── knowledge.json       # 10 条预设方案
│   └── standard_products.json # 标准品列表
├── static/
│   └── index.html           # 单页前端
└── README.md
```

## 校验

```bash
python validate_keywords.py data/knowledge.json
```

## 技术栈

| 层 | 选型 |
|---|---|
| 前端 | HTML5 + Vue.js 3 CDN |
| 后端 | Python FastAPI |
| 硬件通信 | Web Serial API + esptool-js (CDN) |
| 匹配 | 子串包含匹配，零依赖 |
| 存储 | JSON 静态文件 |

## 10 个预设方案

### 通用场景（5 个）
1. 天黑自动亮灯 — 光敏电阻 + LED
2. 自动浇花 — 土壤湿度传感器 + 水泵
3. 温湿度计 — DHT11
4. 桌面小风扇 — DHT11 + 直流风扇
5. 音乐盒 — 按钮 + 无源蜂鸣器

### 非标场景（5 个）
6. 驱猫器 — PIR + 超声波蜂鸣器（34kHz）
7. 生日礼物盒 — 微动开关 + LED 灯带 + 蜂鸣器 + OLED
8. 吃药提醒装置 — RTC + 蜂鸣器 + 按钮
9. 鱼缸自动喂食器 — 步进电机 + RTC
10. 防盗报警器 — 门窗磁 + GSM SIM800L

## 约束

- 芯片：锁定 ESP32-S3
- 匹配：子串包含匹配，不引入 NLP/分词
- 方案生成：预设方案 100% 正确，不调用 LLM
- 浏览器：Chrome/Edge 89+（需 Web Serial API）
