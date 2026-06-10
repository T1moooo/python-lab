# ============================================================
# Day 6 练习：添加编辑角色
# ============================================================
#
# 目标：巩固多 Agent 协作和角色设计
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   添加一个"编辑"角色，流程变为：
#   研究员 → 写手 → 审稿人 → 编辑 → 最终文章
#
#   编辑的职责：
#   - 根据审稿意见修改文章
#   - 优化语言表达
#   - 确保文章流畅
#
# 涉及知识点：
#   - 字典操作
#   - 字符串格式化
#   - 多 Agent 协作


import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


# ========== Agent 角色定义 ==========

AGENTS = {
    "researcher": {
        "name": "研究员",
        "system_prompt": "你是一个研究员。收集和整理信息。"
    },
    "writer": {
        "name": "写手",
        "system_prompt": "你是一个写手。根据资料撰写文章。"
    },
    "reviewer": {
        "name": "审稿人",
        "system_prompt": "你是一个审稿人。检查文章质量，提出修改建议。"
    },
    # TODO 1: 添加编辑角色
    # 提示：
    #   - key 是 "editor"
    #   - "name" 是 "编辑"
    #   - "system_prompt" 描述编辑的职责：根据审稿意见修改文章，优化语言表达
    "editor": {
        "name": "编辑",
        "system_prompt": """你是一个编辑。你的职责是：
1. 根据审稿意见修改文章
2. 优化语言表达
3. 确保文章流畅易读

输出修改后的完整文章。"""
    }
}


# ========== 调用 LLM ==========

def call_llm(role: str, content: str) -> str:
    agent = AGENTS[role]
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": agent["system_prompt"]},
            {"role": "user", "content": content},
        ],
    )
    return response.choices[0].message.content


# ========== 多 Agent 协作流程 ==========

def multi_agent_write(topic: str) -> dict:
    results = {}

    print(f"\n{'='*50}")
    print(f"主题: {topic}")
    print('='*50)

    # 第一步：研究员
    print("\n[研究员] 正在收集资料...")
    research = call_llm("researcher", f"请研究以下主题：{topic}")
    results["research"] = research
    print(f"[研究员] 完成\n{research[:200]}...\n")

    # 第二步：写手
    print("[写手] 正在撰写文章...")
    article = call_llm("writer", f"根据以下资料撰写文章：\n\n{research}")
    results["article_v1"] = article
    print(f"[写手] 初稿完成\n{article[:200]}...\n")

    # 第三步：审稿人
    print("[审稿人] 正在评审...")
    review = call_llm("reviewer", f"请评审以下文章：\n\n{article}")
    results["review"] = review
    print(f"[审稿人] 评审完成\n{review[:200]}...\n")

    # TODO 2: 添加编辑步骤
    # 提示：
    #   - 调用 call_llm("editor", ...)
    #   - 输入：原文 + 审稿意见
    #   - 保存到 results["article_v2"]

    # TODO: 补全这里
    print("[编辑] 正在根据审稿意见修改...")
    edited_article = call_llm("editor", f"请根据审稿意见修改文章：\n\n原文：\n{article}\n\n审稿意见：\n{review}")
    results["article_v2"] = edited_article
    print(f"[编辑] 修改完成\n{edited_article[:200]}...\n")

    # 返回最终结果
    # TODO 3: 修改返回值，返回编辑后的文章
    # 提示：results["final"] 应该是编辑后的文章

    return results


# ========== 主程序 ==========

if __name__ == "__main__":
    print("练习 Multi-Agent Writing Team 启动\n")
    print("角色：研究员 → 写手 → 审稿人 → 编辑\n")

    while True:
        topic = input("输入文章主题 (quit 退出): ")
        if topic.strip().lower() == "quit":
            print("再见！")
            break

        results = multi_agent_write(topic)

        print(f"\n{'='*50}")
        print("最终文章:")
        print('='*50)
        # TODO 4: 打印编辑后的文章
        # 提示：从 results 中取编辑后的文章
        print(results["article_v2"])

        print()
