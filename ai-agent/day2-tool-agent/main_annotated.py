# ============================================================
# Day 2: Tool Agent — 详细注释版
# ============================================================
#
# 这个文件和 main.py 功能完全一样
# 但每一行都有详细注释，帮助你理解每个语法和概念
# 建议先看 main.py 了解整体逻辑，再看这个文件理解细节


# ------------------------------------------------------------
# 第一部分：导入模块
# ------------------------------------------------------------

# json 是 Python 标准库，用来解析 JSON 字符串
# AI 返回的工具参数是 JSON 字符串格式，我们需要把它转成 Python 字典
import json

# os 和 dotenv 用于读取 .env 文件中的 API key（Day 1 学过）
import os
from dotenv import load_dotenv

# openai SDK，用于调用 OpenRouter API（Day 1 学过）
from openai import OpenAI


# ------------------------------------------------------------
# 第二部分：初始化
# ------------------------------------------------------------

# 加载 .env 文件
load_dotenv()

# 创建 OpenAI 客户端
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# 指定使用的模型
MODEL = "openai/gpt-oss-120b:free"


# ------------------------------------------------------------
# 第三部分：定义工具函数
# ------------------------------------------------------------
#
# 什么是"工具"（Tool）？
#   工具就是普通的 Python 函数，但我们会"告诉" AI 这些函数的存在
#   AI 在对话中如果觉得需要调用某个工具，就会"请求"我们去执行它
#   我们执行后把结果返回给 AI，AI 再根据结果生成回复
#
# 这就是 Agent 的核心能力之一：AI 不只是聊天，还能"做事"

def get_weather(city: str) -> str:
    """获取指定城市的天气

    参数:
        city: 城市名称，如 "Beijing"、"Shanghai"

    返回:
        天气信息字符串

    注意:
        这是一个模拟函数，实际项目中会调用真实的天气 API
    """
    # 这里返回固定数据，实际项目会调用真实 API
    return f"Weather in {city}: 25°C, sunny"


def calculate(expression: str) -> str:
    """计算数学表达式

    参数:
        expression: 数学表达式字符串，如 "2 + 3 * 4"

    返回:
        计算结果的字符串形式

    注意:
        eval() 可以执行任意 Python 代码，有安全风险
        这里仅用于学习，生产环境应该用更安全的方式
    """
    # eval() 会把字符串当作 Python 代码执行
    # 例如 eval("2 + 3 * 4") 会返回 14
    return str(eval(expression))


def search_notes(keyword: str) -> str:
    """搜索笔记

    参数:
        keyword: 搜索关键词

    返回:
        搜索结果字符串

    注意:
        这是一个模拟函数，实际项目中会搜索真实的笔记数据库
    """
    return f"Found 3 notes containing '{keyword}'"


# ------------------------------------------------------------
# 第四部分：工具注册表
# ------------------------------------------------------------
#
# TOOLS 是一个字典，把函数名映射到函数对象
#
# 为什么要这样做？
#   AI 返回的工具调用请求里只有函数名（字符串），如 "get_weather"
#   我们需要通过这个字符串找到对应的函数来执行
#   字典的 key 是字符串，value 是函数对象
#
# 什么是"函数对象"？
#   在 Python 中，函数也是对象，可以赋值给变量
#   get_weather 是函数名，不加括号就是函数对象本身
#   get_weather("Beijing") 是调用函数，加括号才执行
TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes,
}


# ------------------------------------------------------------
# 第五部分：定义工具的 JSON Schema
# ------------------------------------------------------------
#
# 这是告诉 AI "有哪些工具可用"的关键部分
#
# 什么是 JSON Schema？
#   JSON Schema 是一种描述 JSON 数据结构的标准格式
#   它告诉 AI：
#   - 工具的名字是什么
#   - 工具是干什么的（description）
#   - 需要哪些参数，每个参数是什么类型
#   - 哪些参数是必填的
#
# 为什么需要这个？
#   AI 模型本身不知道你写了哪些函数
#   你需要用一种标准化的格式"描述"给它听
#   这样 AI 才能决定什么时候调用哪个工具，传什么参数
#
# 这个列表会作为 tools 参数传给 API
TOOLS_SCHEMA = [
    {
        # type: "function" 表示这是一个函数类型的工具
        "type": "function",
        "function": {
            # name: 函数名，必须和 TOOLS 字典里的 key 一致
            "name": "get_weather",
            # description: 告诉 AI 这个函数是干什么的
            # AI 会根据这个描述决定是否调用
            "description": "Get the current weather for a city",
            # parameters: 描述函数接受的参数
            "parameters": {
                "type": "object",
                "properties": {
                    # 每个参数用 key 描述
                    "city": {
                        "type": "string",  # 参数类型
                        "description": "The city name",  # 参数说明
                    }
                },
                # required: 哪些参数是必填的
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


# ------------------------------------------------------------
# 第六部分：主循环
# ------------------------------------------------------------

# 初始化对话历史，包含 system 指令
history = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when needed."}
]

print("Tool Agent 已启动，输入 quit 退出\n")

while True:
    # --------------------------------------------------------
    # 6.1 读取用户输入
    # --------------------------------------------------------
    user_input = input("You: ")

    if user_input.strip().lower() == "quit":
        print("再见！")
        break

    history.append({"role": "user", "content": user_input})

    # --------------------------------------------------------
    # 6.2 第一次 API 调用：让 AI 决定是否需要工具
    # --------------------------------------------------------
    #
    # 这次调用比 Day 1 多了一个参数：tools
    # tools=TOOLS_SCHEMA 告诉 AI 有哪些工具可用
    # AI 会根据用户的问题和工具描述，决定是否需要调用工具
    #
    # 可能的结果：
    #   1. AI 觉得不需要工具 → 直接回复文字
    #   2. AI 觉得需要工具 → 返回 tool_calls 请求
    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
        tools=TOOLS_SCHEMA,  # 关键参数：告诉 AI 有哪些工具
    )

    # response.choices[0].message 是 AI 返回的消息对象
    message = response.choices[0].message

    # --------------------------------------------------------
    # 6.3 检查 AI 是否要求调用工具
    # --------------------------------------------------------
    #
    # message.tool_calls 是一个列表
    # 如果 AI 不需要调用工具，tool_calls 为 None 或空列表
    # 如果 AI 需要调用工具，tool_calls 里会包含一个或多个工具调用请求
    if message.tool_calls:
        # ----------------------------------------------------
        # 6.3a AI 要求调用工具
        # ----------------------------------------------------

        # 先把 AI 的消息加入历史
        # 这条消息包含 tool_calls 信息，必须保存
        # 否则后面 AI 不知道自己之前要求调用了什么
        history.append(message)

        # 逐个执行 AI 要求的工具调用
        # AI 可能一次请求调用多个工具
        for tool_call in message.tool_calls:
            # tool_call.function.name 是 AI 想调用的函数名
            # 例如 "get_weather"
            func_name = tool_call.function.name

            # tool_call.function.arguments 是 AI 传的参数，JSON 字符串格式
            # 例如 '{"city": "Beijing"}'
            # json.loads() 把 JSON 字符串转成 Python 字典
            # 例如 {"city": "Beijing"}
            func_args = json.loads(tool_call.function.arguments)

            # 打印工具调用信息，方便观察
            print(f"  [调用工具] {func_name}({func_args})")

            # 通过工具注册表找到函数并执行
            # TOOLS[func_name] 通过函数名找到函数对象
            # **func_args 把字典展开为关键字参数
            # 例如 **{"city": "Beijing"} 等价于 city="Beijing"
            result = TOOLS[func_name](**func_args)

            # 把工具执行结果加入历史
            # role: "tool" 表示这是工具返回的结果
            # tool_call_id: 必须和 tool_call.id 对应，告诉 AI 这是哪个工具调用的结果
            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # ----------------------------------------------------
        # 6.3b 把工具结果发给 AI，生成最终回复
        # ----------------------------------------------------
        #
        # 现在 history 里包含了：
        #   - system 消息
        #   - 用户的问题
        #   - AI 的 tool_calls 请求
        #   - 工具执行结果
        #
        # 我们再调一次 API，让 AI 根据工具结果生成最终回复
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=history,
        )

        final_message = final_response.choices[0].message.content
        print(f"AI: {final_message}\n")
        history.append({"role": "assistant", "content": final_message})

    else:
        # ----------------------------------------------------
        # 6.3c AI 不需要调用工具，直接回复
        # ----------------------------------------------------
        reply = message.content
        print(f"AI: {reply}\n")
        history.append({"role": "assistant", "content": reply})
