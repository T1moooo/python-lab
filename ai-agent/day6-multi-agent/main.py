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
        "system_prompt": """你是一个研究员。你的职责是：
1. 分析主题，找出关键信息
2. 收集相关数据和事实
3. 整理成结构化的研究报告

输出格式：
- 主题概述
- 关键要点（3-5个）
- 相关数据/事实
- 总结"""
    },
    "writer": {
        "name": "写手",
        "system_prompt": """你是一个写手。你的职责是：
1. 根据研究员提供的资料撰写文章
2. 确保文章结构清晰、逻辑通顺
3. 使用通俗易懂的语言

输出格式：
- 标题
- 引言
- 正文（分段落）
- 结论"""
    },
    "reviewer": {
        "name": "审稿人",
        "system_prompt": """你是一个审稿人。你的职责是：
1. 检查文章的事实准确性
2. 评估文章结构和逻辑
3. 提出修改建议

输出格式：
- 事实准确性评分（1-10）
- 结构评分（1-10）
- 优点
- 需要改进的地方
- 修改建议"""
    }
}


# ========== 调用 LLM ==========

def call_llm(role: str, content: str) -> str:
    """调用 LLM，指定角色

    参数:
        role: Agent 角色（researcher/writer/reviewer）
        content: 输入内容

    返回:
        AI 回复
    """
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
    """多 Agent 协作写作

    流程：
    1. 研究员收集资料
    2. 写手撰写文章
    3. 审稿人评审
    4. 写手根据反馈修改

    返回:
        包含所有中间结果的字典
    """
    results = {}

    print(f"\n{'='*50}")
    print(f"主题: {topic}")
    print('='*50)

    # 第一步：研究员收集资料
    print("\n[研究员] 正在收集资料...")
    research = call_llm("researcher", f"请研究以下主题：{topic}")
    results["research"] = research
    print(f"[研究员] 完成\n{research[:200]}...\n")

    # 第二步：写手撰写文章
    print("[写手] 正在撰写文章...")
    article = call_llm("writer", f"根据以下资料撰写文章：\n\n{research}")
    results["article_v1"] = article
    print(f"[写手] 初稿完成\n{article[:200]}...\n")

    # 第三步：审稿人评审
    print("[审稿人] 正在评审...")
    review = call_llm("reviewer", f"请评审以下文章：\n\n{article}")
    results["review"] = review
    print(f"[审稿人] 评审完成\n{review[:200]}...\n")

    # 第四步：写手修改
    print("[写手] 正在根据反馈修改...")
    revised_article = call_llm("writer", f"请根据审稿意见修改文章：\n\n原文：\n{article}\n\n审稿意见：\n{review}")
    results["article_v2"] = revised_article
    print(f"[写手] 修改完成\n{revised_article[:200]}...\n")

    return results


# ========== 主程序 ==========

if __name__ == "__main__":
    print("Multi-Agent Writing Team 启动\n")
    print("角色：研究员 → 写手 → 审稿人 → 写手（修改）\n")

    while True:
        topic = input("输入文章主题 (quit 退出): ")
        if topic.strip().lower() == "quit":
            print("再见！")
            break

        results = multi_agent_write(topic)

        print(f"\n{'='*50}")
        print("最终文章:")
        print('='*50)
        print(results["article_v2"])
        print()
