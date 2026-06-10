# ============================================================
# Day 1 练习参考答案
# ============================================================
# 建议：先自己写，卡住了再看这个文件


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
    """让 AI 总结之前的对话历史。"""

    # 构造一个专门用于总结的请求
    # 注意：我们不修改原始 history，而是创建一个新的消息列表
    summary_messages = [
        {
            "role": "system",
            "content": "Summarize the following conversation in 2-3 sentences."
        },
        {
            "role": "user",
            "content": str(messages)  # 把历史列表转成字符串发给 AI
        }
    ]

    # 调用 API
    response = client.chat.completions.create(
        model=MODEL,
        messages=summary_messages,
    )

    # 返回总结文本
    return response.choices[0].message.content


while True:
    user_input = input("You: ")

    if user_input.strip().lower() == "quit":
        print("再见！")
        break

    history.append({"role": "user", "content": user_input})

    # 检查对话长度
    # len(history) 包含 system 消息，所以减去 1
    non_system_count = len(history) - 1

    if non_system_count > 6:
        # 获取总结
        summary = summarize_history(history)

        # 重建 history：保留 system 消息 + 总结
        history = [
            history[0],  # 保留原来的 system 指令
            {
                "role": "user",
                "content": f"以下是之前的对话总结，请基于此继续对话：\n{summary}"
            }
        ]

        print("[已总结历史对话]\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=history,
    )

    reply = response.choices[0].message.content
    print(f"AI: {reply}\n")

    history.append({"role": "assistant", "content": reply})
