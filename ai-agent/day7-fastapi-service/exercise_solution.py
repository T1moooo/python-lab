# ============================================================
# Day 7 练习参考答案
# ============================================================
# 建议：先自己写，卡住了再看这个文件


import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"

app = FastAPI(title="Agent API", version="1.0.0")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    timestamp: str


class RateLimiter:
    """简单的限流器"""
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {client_ip: [timestamp1, timestamp2, ...]}

    def is_allowed(self, client_ip: str) -> bool:
        current_time = time.time()

        # 初始化
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # 过滤掉超过窗口时间的旧请求
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if current_time - t < self.window_seconds
        ]

        # 检查是否超过限制
        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        # 添加当前请求
        self.requests[client_ip].append(current_time)
        return True


rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


def call_llm(system_prompt: str, user_message: str) -> str:
    """调用 LLM（带超时）"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            timeout=10,  # 10秒超时
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口（带限流）"""
    # 检查限流
    client_ip = "default"  # 实际项目中从请求中获取
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests")

    logger.info(f"Chat request: {request.message[:50]}...")

    try:
        reply = call_llm("You are a helpful assistant.", request.message)
        timestamp = datetime.now().isoformat()
        return ChatResponse(reply=reply, timestamp=timestamp)
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
