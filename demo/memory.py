"""
记忆管理模块 — 长期记忆 + 短期记忆
持久化存储在 data/memory.json
"""

import json
import os
import time
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")

DEFAULT_MEMORY = {
    "long_term": [],
    "short_term": []
}

# 预置长期记忆（领域知识）
SEED_MEMORIES = [
    # ESP32-S3
    {"content": "ESP32-S3 是双核 Xtensa LX7 处理器，240MHz，512KB SRAM，16MB Flash，支持 WiFi 和 BLE", "tags": ["esp32", "硬件"]},
    {"content": "ESP32-S3 ADC 引脚: GPIO1-GPIO10，量程 0-3.3V，12位分辨率（0-4095）", "tags": ["esp32", "adc", "引脚"]},
    {"content": "ESP32-S3 默认 I2C 引脚: SCL=GPIO22, SDA=GPIO21", "tags": ["esp32", "i2c", "引脚"]},
    {"content": "ESP32-S3 默认 UART0 引脚: TX=GPIO44, RX=GPIO43", "tags": ["esp32", "uart", "引脚"]},
    # MicroPython
    {"content": "MicroPython 的 Pin 类: from machine import Pin; led = Pin(5, Pin.OUT); led.on()", "tags": ["micropython", "gpio"]},
    {"content": "MicroPython 的 ADC 类: from machine import Pin, ADC; adc = ADC(Pin(36)); adc.atten(3); val = adc.read()", "tags": ["micropython", "adc"]},
    {"content": "MicroPython 的 SoftI2C 类: from machine import Pin, SoftI2C; i2c = SoftI2C(scl=Pin(22), sda=Pin(21))", "tags": ["micropython", "i2c"]},
    # 电子元件
    {"content": "DHT11 温湿度传感器: VCC→3.3V, GND→GND, DATA→GPIO，数据脚需 4.7kΩ-10kΩ 上拉电阻到 3.3V", "tags": ["dht11", "温湿度", "接线"]},
    {"content": "光敏电阻模块（模拟）: AO→ADC引脚, VCC→3.3V, GND→GND。光线越暗 ADC 值越大", "tags": ["光敏电阻", "ldr", "接线"]},
    {"content": "PIR 人体红外传感器 HC-SR501: VCC→5V, GND→GND, OUT→GPIO。检测到人时输出高电平", "tags": ["pir", "人体红外", "接线"]},
    {"content": "有源蜂鸣器: VCC→GPIO, GND→GND。GPIO 高电平即响。有源=通电就响，无源=需 PWM 驱动", "tags": ["蜂鸣器", "buzzer", "接线"]},
    {"content": "步进电机 28BYJ-48 + ULN2003 驱动板: IN1→GPIO5, IN2→GPIO18, IN3→GPIO19, IN4→GPIO21, VCC→5V, GND→GND", "tags": ["步进电机", "28byj-48", "接线"]},
    {"content": "土壤湿度传感器（模拟）: AO→ADC引脚, VCC→3.3V/5V, GND→GND。越湿 ADC 值越低", "tags": ["土壤湿度", "接线"]},
    {"content": "OLED 显示屏 SSD1306 I2C: VCC→3.3V, GND→GND, SCL→GPIO22, SDA→GPIO21（I2C 地址通常 0x3C）", "tags": ["oled", "ssd1306", "接线"]},
    {"content": "DS3231 RTC 时钟模块 I2C: VCC→3.3V, GND→GND, SCL→GPIO22, SDA→GPIO21（I2C 地址 0x68）", "tags": ["ds3231", "rtc", "接线"]},
    {"content": "SIM800L GSM 模块: 需独立 3.7V-4.2V 电源（不能直接接 3.3V/5V），UART TX→RX, RX→TX", "tags": ["sim800l", "gsm", "接线"]},
    {"content": "继电器模块: VCC→3.3V/5V, GND→GND, IN→GPIO。高电平触发导通（可控制 220V 设备）", "tags": ["继电器", "relay", "接线"]},
    {"content": "LED 需要串联限流电阻（220Ω-1kΩ），长脚正极接 GPIO，短脚负极通过电阻接 GND", "tags": ["led", "电阻", "接线"]},
    # 平台
    {"content": "本平台有 10 个预设方案: 天黑自动亮灯、自动浇花、温湿度计、桌面小风扇、音乐盒、驱猫器、生日礼物盒、吃药提醒装置、鱼缸自动喂食器、防盗报警器", "tags": ["平台", "方案", "预设"]},
    {"content": "所有方案推荐芯片为 ESP32-S3，使用 MicroPython 编程", "tags": ["平台", "esp32", "micropython"]},
]


def _ensure_file():
    """确保 memory.json 存在，首次自动写入预置知识"""
    if not os.path.exists(MEMORY_FILE):
        mem = DEFAULT_MEMORY.copy()
        mem["long_term"] = []
        for m in SEED_MEMORIES:
            mem["long_term"].append({
                "id": f"lt-{int(time.time())}-{len(mem['long_term'])}",
                "content": m["content"],
                "tags": m["tags"],
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        mem["short_term"] = []
        _write(mem)


def _read() -> dict:
    _ensure_file()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------- 公开 API --------

def add_memory(content: str, tags: list = None, memory_type: str = "long_term") -> dict:
    """添加一条记忆"""
    data = _read()
    mem = {
        "id": f"{'lt' if memory_type == 'long_term' else 'st'}-{int(time.time())}",
        "content": content,
        "tags": tags or [],
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    data[memory_type].append(mem)
    _write(data)
    return mem


def list_memories(memory_type: str = None, tag: str = None) -> dict:
    """列出记忆"""
    data = _read()
    result = {}
    types = ["long_term", "short_term"] if memory_type is None else [memory_type]
    for t in types:
        items = data[t]
        if tag:
            items = [m for m in items if tag in m.get("tags", [])]
        result[t] = items
    return result


def search_memories(query: str, memory_type: str = None) -> list:
    """搜索记忆（子串匹配）"""
    data = _read()
    results = []
    types = ["long_term", "short_term"] if memory_type is None else [memory_type]
    q = query.lower()
    for t in types:
        for m in data[t]:
            if q in m["content"].lower() or q in " ".join(m.get("tags", [])).lower():
                results.append({**m, "_type": t})
    return results


def delete_memory(memory_id: str) -> bool:
    """按 ID 删除记忆"""
    data = _read()
    for t in ["long_term", "short_term"]:
        for i, m in enumerate(data[t]):
            if m["id"] == memory_id:
                data[t].pop(i)
                _write(data)
                return True
    return False


def build_memory_context(user_message: str) -> str:
    """根据用户输入构建记忆上下文文本，注入对话"""
    # 搜索相关长期记忆
    related = search_memories(user_message, memory_type="long_term")
    if not related:
        return ""

    lines = ["[参考记忆]"]
    for m in related[:6]:  # 最多 6 条
        lines.append(f"- {m['content']}")
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print(f"长期记忆: {len(list_memories('long_term')['long_term'])} 条")
    print(f"短期记忆: {len(list_memories('short_term')['short_term'])} 条")
    print()
    r = search_memories("DHT11")
    print(f"搜索 'DHT11': {len(r)} 条")
    for m in r:
        print(f"  [{m['_type']}] {m['content'][:60]}...")
