# ============================================================
# Day 7: FastAPI Agent Service — 详细注释版
# ============================================================
#
# 今天学习"部署"：把 Agent 包装成 API 服务
#
# 关键概念：
#   - FastAPI：Python Web 框架，用于创建 API
#   - Uvicorn：ASGI 服务器，用于运行 FastAPI
#   - Pydantic：数据验证库，用于定义请求/响应格式
#   - 日志：记录程序运行状态
#   - API Key 验证：保护接口安全


# ------------------------------------------------------------
# 第一部分：导入模块
# ------------------------------------------------------------

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# FastAPI 相关
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel


# ------------------------------------------------------------
# 第二部分：初始化
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# 第三部分：日志配置
# ------------------------------------------------------------
#
# 什么是日志？
#   日志是程序运行时的记录，类似于"黑匣子"
#   可以帮助我们：
#   - 追踪程序执行流程
#   - 排查错误
#   - 监控性能
#
# 日志级别：
#   DEBUG    → 调试信息
#   INFO     → 一般信息
#   WARNING  → 警告
#   ERROR    → 错误
#   CRITICAL → 严重错误

logging.basicConfig(
    level=logging.INFO,  # 只记录 INFO 及以上级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.FileHandler("app.log"),    # 输出到文件
        logging.StreamHandler()            # 输出到控制台
    }
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# 第四部分：OpenAI 客户端
# ------------------------------------------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


# ------------------------------------------------------------
# 第五部分：FastAPI 应用
# ------------------------------------------------------------
#
# FastAPI 是什么？
#   FastAPI 是一个现代、高性能的 Python Web 框架
#   用于创建 API（应用程序编程接口）
#
# 为什么用 FastAPI？
#   - 自动生成 API 文档
#   - 数据验证（通过 Pydantic）
#   - 异步支持（高性能）
#   - 类型提示（IDE 支持好）

app = FastAPI(title="Agent API", version="1.0.0")


# ------------------------------------------------------------
# 第六部分：数据模型
# ------------------------------------------------------------
#
# Pydantic 的 BaseModel 用于定义数据结构
# 它会自动验证数据类型

class ChatRequest(BaseModel):
    """聊天请求的数据格式"""
    message: str                           # 用户消息（必填）
    system_prompt: str = "You are a helpful assistant."  # 系统提示（可选，有默认值）


class ChatResponse(BaseModel):
    """聊天响应的数据格式"""
    reply: str        # AI 回复
    timestamp: str    # 时间戳


class ResearchRequest(BaseModel):
    """研究请求的数据格式"""
    topic: str        # 研究主题


class ResearchResponse(BaseModel):
    """研究响应的数据格式"""
    research: str     # 研究结果
    article: str      # 文章
    timestamp: str    # 时间戳


# ------------------------------------------------------------
# 第七部分：API Key 验证
# ------------------------------------------------------------
#
# 为什么要验证 API Key？
#   - 防止未授权访问
#   - 限制使用量
#   - 追踪使用者

async def verify_api_key(x_api_key: str = Header(...)):
    """验证 API Key

    FastAPI 的 Depends() 用于依赖注入
    它会在每次请求时自动调用这个函数

    Header(...) 表示从 HTTP Header 中读取值
    ... 表示这个值是必填的
    """
    expected_key = os.getenv("APP_API_KEY", "default-secret-key")

    if x_api_key != expected_key:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")

    return x_api_key


# ------------------------------------------------------------
# 第八部分：工具函数
# ------------------------------------------------------------

def call_llm(system_prompt: str, user_message: str) -> str:
    """调用 LLM

    参数:
        system_prompt: 系统提示
        user_message: 用户消息

    返回:
        AI 回复
    """
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


# ------------------------------------------------------------
# 第九部分：API 路由
# ------------------------------------------------------------
#
# 路由（Route）= URL 路径 + 处理函数
#
# @app.get("/") 表示 GET 请求的路由
# @app.post("/chat") 表示 POST 请求的路由
#
# GET  vs POST：
#   GET  → 获取数据（参数在 URL 里）
#   POST → 提交数据（参数在请求体里）

@app.get("/")
async def root():
    """健康检查接口

    用于测试服务是否正常运行
    访问 http://localhost:8000/ 会返回这个
    """
    return {"status": "ok", "message": "Agent API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口

    接收用户消息，返回 AI 回复

    参数:
        request: ChatRequest 类型，FastAPI 会自动解析请求体

    返回:
        ChatResponse 类型，FastAPI 会自动序列化为 JSON
    """
    logger.info(f"Chat request: {request.message[:50]}...")

    try:
        reply = call_llm(request.system_prompt, request.message)
        timestamp = datetime.now().isoformat()

        logger.info(f"Chat response generated successfully")
        return ChatResponse(reply=reply, timestamp=timestamp)

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        # HTTPException 会返回指定的 HTTP 状态码和错误信息
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest, api_key: str = Depends(verify_api_key)):
    """研究接口（需要 API Key）

    接收研究主题，返回研究结果和文章

    Depends(verify_api_key) 表示：
    在执行这个函数之前，先调用 verify_api_key 验证 API Key
    """
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


# ------------------------------------------------------------
# 第十部分：启动
# ------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Agent API...")
    # uvicorn.run() 启动服务器
    # host="0.0.0.0" 表示监听所有网络接口
    # port=8000 表示监听 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)
