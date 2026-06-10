# ============================================================
# Day 7 练习：添加超时和限流
# ============================================================
#
# 目标：巩固 API 部署和错误处理
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   1. 添加请求超时处理（10秒）
#   2. 添加简单的限流（每分钟最多5个请求）
#
# 涉及知识点：
#   - 时间操作（time）
#   - 字典操作
#   - 异常处理


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


# ========== 数据模型 ==========
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    timestamp: str


# ========== 练习：限流器 ==========
class RateLimiter:
    """简单的限流器（基于计数器）

    功能：限制总请求次数
    """
    def __init__(self, max_requests: int = 5):
        self.max_requests = max_requests
        self.count = 0  # 请求计数器

    def is_allowed(self) -> bool:
        """检查是否允许请求"""
        self.count += 1
        if self.count > self.max_requests:
            return False
        return True

    def reset(self):
        """重置计数器"""
        self.count = 0


# 创建限流器实例
rate_limiter = RateLimiter(max_requests=5)


# ========== 工具函数 ==========
def call_llm(system_prompt: str, user_message: str) -> str:
    """调用 LLM（带超时）"""
    # TODO 3: 添加超时处理
    # 提示：
    #   - 在 client.chat.completions.create() 调用中添加 timeout 参数
    #   - timeout=10 表示 10 秒超时
    #   - 用 try-except 捕获超时异常

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            timeout=10,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ========== API 路由 ==========
@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口（带限流）"""
    # 检查限流
    if not rate_limiter.is_allowed():
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
