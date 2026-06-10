# ============================================================
# Day 2 练习：添加一个新工具
# ============================================================
#
# 目标：巩固 function calling 的完整流程
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   在 main.py 的基础上，添加一个新工具：
#   - translate(text, target_language) — 翻译文本（模拟返回固定结果）
#
#   你需要：
#   1. 写一个 translate 函数
#   2. 把它加入 TOOLS 字典
#   3. 把它的 Schema 加入 TOOLS_SCHEMA
#
# 涉及知识点：
#   - 函数定义
#   - 字典操作
#   - JSON Schema 编写
#   - function calling 完整流程


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


# TODO 1: 定义 translate 函数
# 参数：text (str) - 要翻译的文本
# 参数：target_language (str) - 目标语言
# 返回：翻译结果字符串（模拟返回，如 "Translated '{text}' to {target_language}: ..."）
# 提示：
#   - 函数体直接返回一个格式化的字符串即可
#   - 用 f-string 格式化返回值
def translate(text:str, target_language:str) -> str:
    return f"Translated '{text}' to {target_language}:[模拟翻译结果]"

# TODO: 补全这里


# ========== 工具注册表 ==========

TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes,
    # TODO 2: 把 translate 加入 TOOLS 字典
    # 提示：key 是函数名字符串，value 是函数对象（不加括号）
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
    # TODO 3: 添加 translate 的 Schema
    # 提示：
    #   - 复制上面任意一个工具的格式
    #   - name 必须是 "translate"
    #   - description 告诉 AI 这个工具是翻译文本用的
    #   - parameters 包含两个属性：text 和 target_language，都是 string 类型
    #   - required 两个都是必填的

    # TODO: 补全这里
    {
        "type": "function",
        "function": {
            "name": "translate",
            "description": "Translate text to a target language",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to translate"},
                    "target_language": {"type": "string", "description": "The language to translate to"}
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
