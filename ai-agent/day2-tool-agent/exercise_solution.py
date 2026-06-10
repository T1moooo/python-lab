# ============================================================
# Day 2 练习参考答案
# ============================================================
# 建议：先自己写，卡住了再看这个文件


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


# ========== 工具函数 ==========

def get_weather(city: str) -> str:
    return f"Weather in {city}: 25°C, sunny"


def calculate(expression: str) -> str:
    return str(eval(expression))


def search_notes(keyword: str) -> str:
    return f"Found 3 notes containing '{keyword}'"


def translate(text: str, target_language: str) -> str:
    """翻译文本（模拟）"""
    return f"Translated '{text}' to {target_language}: [模拟翻译结果]"


# ========== 工具注册表 ==========

TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes,
    "translate": translate,
}

# ========== 工具 Schema ==========

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"}
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
                    "expression": {"type": "string", "description": "The math expression to calculate"}
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
                    "keyword": {"type": "string", "description": "The keyword to search for"}
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "translate",
            "description": "Translate text to a target language",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to translate"},
                    "target_language": {"type": "string", "description": "The target language, e.g. 'Chinese', 'French'"},
                },
                "required": ["text", "target_language"],
            },
        },
    },
]


# ========== 主循环 ==========

history = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when needed."}
]

print("练习 Tool Agent 已启动，输入 quit 退出\n")

while True:
    user_input = input("You: ")

    if user_input.strip().lower() == "quit":
        print("再见！")
        break

    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
        tools=TOOLS_SCHEMA,
    )

    message = response.choices[0].message

    if message.tool_calls:
        history.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  [调用工具] {func_name}({func_args})")

            result = TOOLS[func_name](**func_args)

            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        final_response = client.chat.completions.create(
            model=MODEL,
            messages=history,
        )

        final_message = final_response.choices[0].message.content
        print(f"AI: {final_message}\n")
        history.append({"role": "assistant", "content": final_message})

    else:
        reply = message.content
        print(f"AI: {reply}\n")
        history.append({"role": "assistant", "content": reply})
