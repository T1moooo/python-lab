# ============================================================
# Day 1 练习：给 Chatbot 加上"记忆摘要"功能
# ============================================================
#
# 目标：巩固今天学的 Python 基础和 API 调用
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   在基础 chatbot 上增加一个功能：
#   每当对话超过 6 条消息（不算 system 消息），就让 AI 总结之前的对话
#   然后用这个总结替代之前的历史消息，节省 token
#
# 涉及知识点：
#   - 列表操作（len、切片、append）
#   - 条件判断（if）
#   - 字符串格式化（f-string）
#   - API 调用
#   - 字典操作


import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "google/gemini-2.0-flash-exp:free"

history = [
    {"role": "system", "content": "You are a helpful Python tutor."}
]

print("练习 Chatbot 已启动，输入 quit 退出\n")
print("功能：对话超过 6 条时自动总结历史\n")


def summarize_history(messages):
    """
    让 AI 总结之前的对话历史。

    参数:
        messages: 对话历史列表（包含 system 消息）

    返回:
        总结后的字符串
    """
    # TODO 1: 构造一个总结请求
    # 提示：
    #   - 创建一个新的消息列表 summary_messages
    #   - 第一条：system 消息，内容为 "Summarize the following conversation in 2-3 sentences."
    #   - 第二条：user 消息，内容是把 messages 转成字符串（用 str(messages)）
    #   - 调用 client.chat.completions.create()，传入 summary_messages
    #   - 返回 AI 的回复文本

    summary_messages = [
        # TODO: 补全这里
    ]

    # TODO: 调用 API 获取总结

    # TODO: 返回总结文本
    pass


while True:
    user_input = input("You: ")

    if user_input.strip().lower() == "quit":
        print("再见！")
        break

    history.append({"role": "user", "content": user_input})

    # TODO 2: 检查对话长度，如果超过阈值就总结
    # 提示：
    #   - len(history) 获取列表长度
    #   - 减去 1 就是"非 system 消息"的数量（因为只有第一条是 system）
    #   - 如果非 system 消息 > 6：
    #       - 调用 summarize_history(history) 获取总结
    #       - 重建 history：保留 system 消息 + 一条新的 user 消息（内容是总结）
    #       - 打印 "[已总结历史对话]"
    #   - 切片语法：history[0] 取第一条，history[1:5] 取第 2~5 条

    # TODO: 补全这里

    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
    )

    reply = response.choices[0].message.content
    print(f"AI: {reply}\n")

    history.append({"role": "assistant", "content": reply})
