"""
单片机创意平台 — FastAPI 后端
仅提供 /generate 接口
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os

from matcher import process as match_process
from agent import chat_with_agent
from memory import add_memory, list_memories, search_memories, delete_memory

app = FastAPI(title="单片机创意平台", version="0.1.0")

# 挂载静态文件
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class GenerateRequest(BaseModel):
    text: str
    skip_standard: bool = False


class GenerateResponse(BaseModel):
    type: str
    message: str = ""
    scheme: dict = None
    product: dict = None
    troubleshooting: list = None
    score: float = 0.0
    score_details: list = None


class AgentChatRequest(BaseModel):
    messages: list
    temperature: float = 0.7


class AgentChatResponse(BaseModel):
    reply: str


@app.get("/")
def root():
    """返回前端页面"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "单片机创意平台 API 运行中 — 请访问 /static/index.html"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """接收用户创意，返回匹配结果"""
    if not req.text or not req.text.strip():
        return GenerateResponse(
            type="error",
            message="请输入你的创意"
        )

    result = match_process(req.text.strip(), skip_standard=req.skip_standard)
    return GenerateResponse(**result)


@app.post("/api/agent/chat", response_model=AgentChatResponse)
def agent_chat(req: AgentChatRequest):
    """AI 助手对话接口"""
    reply = chat_with_agent(req.messages, temperature=req.temperature)
    return AgentChatResponse(reply=reply)


# -------- 记忆管理接口 --------

class MemoryAddRequest(BaseModel):
    content: str
    tags: list = []
    memory_type: str = "long_term"


class MemoryDeleteRequest(BaseModel):
    memory_id: str


@app.get("/api/agent/memory")
def api_list_memories(memory_type: str = None, tag: str = None, query: str = None):
    """列出或搜索记忆"""
    if query:
        results = search_memories(query, memory_type=memory_type)
        return {"results": results, "total": len(results)}
    data = list_memories(memory_type=memory_type, tag=tag)
    total = sum(len(v) for v in data.values())
    return {**data, "total": total}


@app.post("/api/agent/memory")
def api_add_memory(req: MemoryAddRequest):
    """添加一条记忆"""
    mem = add_memory(req.content, tags=req.tags, memory_type=req.memory_type)
    return {"success": True, "memory": mem}


@app.delete("/api/agent/memory")
def api_delete_memory(memory_id: str):
    """删除一条记忆"""
    ok = delete_memory(memory_id)
    return {"success": ok}


if __name__ == "__main__":
    print("=" * 50)
    print("  单片机创意平台 — V0.1 Demo")
    print("  访问地址: http://localhost:8000")
    print("  AI 助手已接入 DeepSeek")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
