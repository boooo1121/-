"""
触发词唯一性校验脚本
运行：python validate_keywords.py data/knowledge.json
退出码 0 = 通过，非 0 = 有冲突
"""

import json
import sys

BLACKLIST_WORDS = [
    "自动", "智能", "控制", "检测", "显示", "模块", "传感器", "设备",
    "系统", "开关", "测量", "监控", "管理", "调节", "感应", "输出",
    "输入", "数据", "信号", "状态", "触发", "执行", "启动", "停止",
    "运行", "处理", "实时", "动态", "静态", "模式", "简单", "简易",
    "快速", "方便", "实用", "多功能", "DIY", "制作", "电子", "电路"
]


def validate(filepath: str) -> bool:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    passed = True
    trigger_map = {}  # word -> scheme_title
    all_triggers = []
    all_boosts = []

    for i, scheme in enumerate(data):
        title = scheme.get("title", f"方案 #{i+1}")
        trigger_words = scheme.get("trigger_words", [])
        boost_words = scheme.get("boost_words", [])

        all_triggers.append((title, trigger_words))
        all_boosts.append((title, boost_words))

        # 检查 trigger_words 数量
        if len(trigger_words) < 2 or len(trigger_words) > 5:
            print(f"[失败] {title}: trigger_words 数量 {len(trigger_words)}，需 2-5 个")
            passed = False

        # 检查 boost_words 数量
        if len(boost_words) < 3 or len(boost_words) > 10:
            print(f"[失败] {title}: boost_words 数量 {len(boost_words)}，需 3-10 个")
            passed = False

        # 检查单字
        for w in trigger_words + boost_words:
            if len(w) < 2:
                print(f"[失败] {title}: 关键词 '{w}' 为单字，禁止")
                passed = False

        # 检查黑名单
        for w in trigger_words + boost_words:
            if w in BLACKLIST_WORDS:
                print(f"[失败] {title}: 关键词 '{w}' 在通用词黑名单中")
                passed = False

        # 检查 trigger_words 唯一性
        for w in trigger_words:
            if w in trigger_map:
                print(f"[失败] 触发词 '{w}' 冲突: 同时出现在 '{trigger_map[w]}' 和 '{title}'")
                passed = False
            else:
                trigger_map[w] = title

    if passed:
        print(f"✅ 校验通过！共 {len(data)} 个方案，{len(trigger_map)} 个唯一触发词")
    else:
        print(f"❌ 校验失败，请修复以上问题")

    return passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python validate_keywords.py <knowledge.json 路径>")
        sys.exit(1)

    success = validate(sys.argv[1])
    sys.exit(0 if success else 1)
