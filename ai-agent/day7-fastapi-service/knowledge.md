# Day 7 知识点整理

## 1. FastAPI 基础

### 1.1 什么是 FastAPI？

FastAPI 是一个现代、高性能的 Python Web 框架，用于创建 API。

```
传统脚本：运行一次就结束
Web API：  一直运行，等待请求，处理后返回响应
```

### 1.2 FastAPI 的核心概念

| 概念 | 说明 |
|------|------|
| `FastAPI()` | 创建应用实例 |
| `@app.get("/")` | 定义 GET 路由 |
| `@app.post("/chat")` | 定义 POST 路由 |
| `BaseModel` | 定义数据模型 |
| `Depends()` | 依赖注入 |

### 1.3 最小示例

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello"}

# 运行：uvicorn main:app --reload
```

---

## 2. 路由（Route）

### 2.1 什么是路由？

路由 = URL 路径 + 处理函数

```python
@app.get("/")           # GET 请求，路径是 /
async def root():
    return {"status": "ok"}

@app.post("/chat")      # POST 请求，路径是 /chat
async def chat():
    return {"reply": "..."}
```

### 2.2 GET vs POST

| 方法 | 用途 | 参数位置 |
|------|------|---------|
| GET | 获取数据 | URL 参数 |
| POST | 提交数据 | 请求体 |

```python
# GET 请求
GET /users?id=123

# POST 请求
POST /chat
Body: {"message": "hello"}
```

---

## 3. Pydantic 数据模型

### 3.1 什么是 Pydantic？

Pydantic 用于数据验证和序列化。

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful assistant."

# 自动验证
request = ChatRequest(message="hello")  # OK
request = ChatRequest(message=123)      # 报错！message 必须是字符串
```

### 3.2 BaseModel 的作用

- 自动验证数据类型
- 自动生成 API 文档
- 自动序列化/反序列化

---

## 4. 日志（Logging）

### 4.1 什么是日志？

日志是程序运行时的记录，帮助追踪和排查问题。

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("这是一条信息")
logger.warning("这是一条警告")
logger.error("这是一条错误")
```

### 4.2 日志级别

| 级别 | 用途 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 一般信息 |
| WARNING | 警告 |
| ERROR | 错误 |
| CRITICAL | 严重错误 |

### 4.3 日志输出

```python
logging.basicConfig(
    handlers=[
        logging.FileHandler("app.log"),    # 输出到文件
        logging.StreamHandler()            # 输出到控制台
    ]
)
```

---

## 5. API Key 验证

### 5.1 为什么需要验证？

- 防止未授权访问
- 限制使用量
- 追踪使用者

### 5.2 FastAPI 的依赖注入

```python
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "expected-key":
        raise HTTPException(status_code=401)
    return x_api_key

@app.post("/research")
async def research(api_key: str = Depends(verify_api_key)):
    # 这里 api_key 已经验证过了
    ...
```

`Depends()` 会在每次请求时自动调用依赖函数。

---

## 6. Uvicorn

### 6.1 什么是 Uvicorn？

Uvicorn 是 ASGI 服务器，用于运行 FastAPI 应用。

```python
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 6.2 启动方式

```bash
# 方式1：代码里启动
python main.py

# 方式2：命令行启动
uvicorn main:app --reload
# main:app 表示 main.py 里的 app 变量
# --reload 表示代码修改后自动重启
```

---

## 7. HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求错误 |
| 401 | 未授权 |
| 404 | 未找到 |
| 500 | 服务器错误 |

```python
raise HTTPException(status_code=401, detail="Invalid API key")
```

---

## 8. Agent 核心概念

### 8.1 Day 1-7 的完整演进

```
Day 1: Agent = LLM + 指令 + 循环
Day 2: Agent = LLM + 指令 + 工具 + 循环
Day 3: Agent = LLM + 指令 + 工具 + 知识库 + 循环
Day 4: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 循环
Day 5: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 自我纠错 + 循环
Day 6: 多 Agent 协作 = 多个 Agent + 角色分工 + 信息传递
Day 7: Agent 服务 = Agent + API + 日志 + 验证 + 部署
```

### 8.2 部署的重要性

```
本地脚本：只能在自己电脑上运行
API 服务：任何人都可以通过网络访问
```

---

## 9. 常见问题

### Q: FastAPI 和 Flask 有什么区别？
A: FastAPI 更现代，支持异步，自动生成文档，性能更好。Flask 更简单，生态更成熟。

### Q: 为什么用 async？
A: async 是异步编程，可以同时处理多个请求，提高性能。

### Q: 如何测试 API？
A: 访问 http://localhost:8000/docs 可以看到自动生成的 API 文档，直接在页面上测试。

### Q: 如何部署到服务器？
A: 可以用 Docker、云服务（AWS、阿里云）等。学习阶段在本地运行即可。
