import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

load_dotenv()

# ========== 日志配置 ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== OpenAI 客户端 ==========
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"

# ========== FastAPI 应用 ==========
app = FastAPI(title="Agent API", version="1.0.0")


# ========== 数据模型 ==========
class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful assistant."


class ChatResponse(BaseModel):
    reply: str
    timestamp: str


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    research: str
    article: str
    timestamp: str


# ========== API Key 验证 ==========
async def verify_api_key(x_api_key: str = Header(...)):
    """验证 API Key"""
    expected_key = os.getenv("APP_API_KEY", "default-secret-key")
    if x_api_key != expected_key:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ========== 工具函数 ==========
def call_llm(system_prompt: str, user_message: str) -> str:
    """调用 LLM"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ========== API 路由 ==========
@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "Agent API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    logger.info(f"Chat request: {request.message[:50]}...")

    try:
        reply = call_llm(request.system_prompt, request.message)
        timestamp = datetime.now().isoformat()

        logger.info(f"Chat response generated successfully")
        return ChatResponse(reply=reply, timestamp=timestamp)

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest, api_key: str = Depends(verify_api_key)):
    """研究接口（需要 API Key）"""
    logger.info(f"Research request: {request.topic}")

    try:
        # 研究员
        research_result = call_llm(
            "You are a researcher. Collect and organize information.",
            f"Research this topic: {request.topic}"
        )

        # 写手
        article = call_llm(
            "You are a writer. Write an article based on the research.",
            f"Write an article based on this research:\n\n{research_result}"
        )

        timestamp = datetime.now().isoformat()

        logger.info(f"Research completed successfully")
        return ResearchResponse(
            research=research_result,
            article=article,
            timestamp=timestamp
        )

    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 启动 ==========
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Agent API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
