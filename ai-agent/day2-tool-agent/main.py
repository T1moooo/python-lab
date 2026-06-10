import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


# ========== 定义工具 ==========

def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"Weather in {city}: 25°C, sunny"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))


def search_notes(keyword: str) -> str:
    """搜索笔记"""
    return f"Found 3 notes containing '{keyword}'"


# 工具注册表：函数名 → 函数对象
TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes,
}


# ========== 定义工具的 JSON Schema（告诉 AI 有哪些工具可用）==========

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to calculate, e.g. '2 + 3 * 4'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Search notes by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for",
                    }
                },
                "required": ["keyword"],
            },
        },
    },
]


# ========== 主循环 ==========

history = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when needed."}
]

print("Tool Agent 已启动，输入 quit 退出\n")

while True:
    user_input = input("You: ")

    if user_input.strip().lower() == "quit":
        print("再见！")
        break

    history.append({"role": "user", "content": user_input})

    # 第一步：让 AI 决定是否调用工具
    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
        tools=TOOLS_SCHEMA,
    )

    message = response.choices[0].message

    # 第二步：检查 AI 是否要求调用工具
    if message.tool_calls:
        # AI 要求调用工具
        # 先把 AI 的消息加入历史（包含 tool_calls 信息）
        history.append(message)

        # 逐个执行工具调用
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  [调用工具] {func_name}({func_args})")

            # 执行工具函数
            result = TOOLS[func_name](**func_args)

            # 把工具结果加入历史
            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # 第三步：把工具结果发给 AI，让 AI 生成最终回复
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=history,
        )

        final_message = final_response.choices[0].message.content
        print(f"AI: {final_message}\n")
        history.append({"role": "assistant", "content": final_message})

    else:
        # AI 不需要调用工具，直接回复
        reply = message.content
        print(f"AI: {reply}\n")
        history.append({"role": "assistant", "content": reply})
