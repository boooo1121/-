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


if __name__ == "__main__":
    print("=" * 50)
    print("  单片机创意平台 — V0.1 Demo")
    print("  访问地址: http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
