"""
匹配引擎 — 负面过滤 + 标准品检测 + 方案匹配
零依赖，纯子串包含匹配
"""

import json
import os
from typing import Optional

# 负面词表（30+ 个）
NEGATIVE_WORDS = [
    "坏了", "不亮", "没反应", "修", "故障", "出问题", "不好使",
    "报废", "烧了", "不工作", "有问题", "不正常", "坏了怎么办",
    "不转了", "没声音", "没显示", "连不上", "不识别", "无法连接",
    "没输出", "短路", "冒烟", "发烫", "没响应", "不动作", "卡住了",
    "报错", "error", "fail", "异常", "失灵", "没用", "不行了"
]

# 通用词黑名单（40 个）
BLACKLIST_WORDS = [
    "自动", "智能", "控制", "检测", "显示", "模块", "传感器", "设备",
    "系统", "开关", "测量", "监控", "管理", "调节", "感应", "输出",
    "输入", "数据", "信号", "状态", "触发", "执行", "启动", "停止",
    "运行", "处理", "实时", "动态", "静态", "模式", "简单", "简易",
    "快速", "方便", "实用", "多功能", "DIY", "制作", "电子", "电路"
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def contains_any(text: str, words: list) -> bool:
    """原始输入是否包含列表中任一子串（不区分大小写）"""
    text_lower = text.lower()
    for w in words:
        if w.lower() in text_lower:
            return True
    return False


def check_negative(text: str, knowledge: list, standard_products: list) -> Optional[dict]:
    """
    步骤 1：负面过滤 + 复合意图判断
    返回：None（未命中）| {"type": "negative"}（拦截）| {"type": "pass"}（放行）
    """
    if not contains_any(text, NEGATIVE_WORDS):
        return None  # 未命中负面词，放行

    # 命中负面词 → 复合意图判断
    # 检查是否同时命中任一方案的 trigger/boost 或标准品关键词
    has_creative_intent = False

    # 检查方案关键词
    for scheme in knowledge:
        all_keywords = scheme.get("trigger_words", []) + scheme.get("boost_words", [])
        if contains_any(text, all_keywords):
            has_creative_intent = True
            break

    # 检查标准品关键词
    if not has_creative_intent:
        for sp in standard_products:
            if contains_any(text, sp.get("keywords", [])):
                has_creative_intent = True
                break

    if has_creative_intent:
        return {"type": "pass"}  # 有创作意图，放行
    else:
        return {"type": "negative"}  # 纯负面，拦截


def check_standard_product(text: str, standard_products: list) -> Optional[dict]:
    """
    步骤 2：标准品检测
    返回：None（未命中）| {"type": "standard", "product": {...}}（劝退）
    """
    text_lower = text.lower()
    for sp in standard_products:
        for kw in sp.get("keywords", []):
            if kw.lower() in text_lower:
                return {
                    "type": "standard",
                    "product": sp
                }
    return None


def compute_score(text: str, scheme: dict) -> float:
    """
    计算方案匹配得分
    触发词必须至少命中一个；权重按位置衰减
    """
    text_lower = text.lower()
    trigger_words = scheme.get("trigger_words", [])
    boost_words = scheme.get("boost_words", [])

    # 检查 trigger_words 是否有命中
    trigger_hits = []
    for i, w in enumerate(trigger_words):
        # 检查是否在文本中
        if w.lower() in text_lower:
            trigger_hits.append(i)

    if not trigger_hits:
        return 0.0  # 没有命中任何触发词，方案无资格

    # 计算 trigger_words 得分：位置靠前权重高
    # 索引 0: 1.0, 索引 1: 0.5, 索引 2: 0.33, 索引 3: 0.25, ...
    trigger_score = 0.0
    for idx in trigger_hits:
        trigger_score += 1.0 / (idx + 1)

    # 计算 boost_words 得分：命中权重为触发词的 30%，同样位置衰减
    boost_score = 0.0
    for i, w in enumerate(boost_words):
        if w.lower() in text_lower:
            boost_score += 0.3 / (i + 1)

    return trigger_score + boost_score


def match_scheme(text: str, knowledge: list) -> Optional[dict]:
    """
    步骤 3：方案匹配
    返回：None（未匹配）| {"type": "match", "scheme": {...}}
    """
    best_scheme = None
    best_score = 0.0
    score_details = []

    for scheme in knowledge:
        score = compute_score(text, scheme)
        score_details.append({
            "title": scheme.get("title", ""),
            "score": round(score, 4)
        })
        if score > best_score:
            best_score = score
            best_scheme = scheme

    if best_scheme and best_score > 0:
        return {
            "type": "match",
            "scheme": best_scheme,
            "score": round(best_score, 4),
            "score_details": score_details
        }
    return None


def process(text: str, skip_standard: bool = False) -> dict:
    """
    匹配流水线入口
    skip_standard: 用户点击"坚持要做"时跳过标准品检测
    """
    knowledge = load_json("knowledge.json")
    standard_products = load_json("standard_products.json")

    # 步骤 1：负面过滤
    negative_result = check_negative(text, knowledge, standard_products)
    if negative_result and negative_result["type"] == "negative":
        return {
            "type": "negative",
            "message": "检测到你的输入更像是故障排查需求",
            "troubleshooting": [
                "检查 USB 数据线（必须支持数据传输，不能是仅充电线）",
                "检查板子上电源指示灯是否亮起",
                "按住 BOOT 键不放 → 按一下 EN 键 → 松开 BOOT 键（进入下载模式）",
                "在设备管理器中检查 COM 端口是否被识别"
            ]
        }

    # 步骤 2：标准品检测（可跳过）
    if not skip_standard:
        standard_result = check_standard_product(text, standard_products)
        if standard_result:
            return standard_result

    # 步骤 3：方案匹配
    match_result = match_scheme(text, knowledge)
    if match_result:
        return match_result

    # 步骤 4：未匹配兜底
    return {
        "type": "no_match",
        "message": "暂未收录该创意，试试换个说法"
    }


if __name__ == "__main__":
    # 简单测试
    test_cases = [
        ("天黑自动亮的台灯", False),
        ("灯不亮了怎么修", False),
        ("我想做个智能插座", False),
        ("帮我做个无人机", False),
        ("灯坏了想做个夜灯", False),
    ]
    for text, skip in test_cases:
        result = process(text, skip)
        print(f"输入: {text}")
        print(f"  类型: {result.get('type')}")
        if result.get("type") == "match":
            print(f"  方案: {result['scheme']['title']} (score={result.get('score')})")
        elif result.get("type") == "standard":
            print(f"  标准品: {result['product']['name']}")
        print()
