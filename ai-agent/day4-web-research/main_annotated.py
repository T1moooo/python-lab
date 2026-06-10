# ============================================================
# Day 4: Web Research Agent — 详细注释版
# ============================================================
#
# 今天学习"多步规划"：Agent 不是一次性回答，而是先规划、再执行、最后总结
#
# 流程：
#   1. 规划（Plan）：AI 分析任务，制定步骤
#   2. 搜索（Search）：根据计划执行搜索
#   3. 阅读（Read）：读取搜索结果
#   4. 总结（Summarize）：综合所有信息生成报告
#
# 为什么需要多步规划？
#   - 复杂问题不能一步到位
#   - 需要分解任务，逐步执行
#   - 这是 Agent 的核心能力之一


# ------------------------------------------------------------
# 第一部分：导入模块
# ------------------------------------------------------------

import os
import json
from dotenv import load_dotenv
from openai import OpenAI


# ------------------------------------------------------------
# 第二部分：初始化
# ------------------------------------------------------------

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


# ------------------------------------------------------------
# 第三部分：模拟工具
# ------------------------------------------------------------
# 真实项目中，web_search 会调用搜索 API（如 Google、Bing）
# read_article 会爬取网页内容
# 这里用模拟数据，聚焦在"多步规划"的概念上

def web_search(query: str) -> str:
    """模拟网页搜索

    参数:
        query: 搜索关键词

    返回:
        搜索结果字符串
    """
    # 模拟搜索结果
    mock_results = {
        "python": "Python is a high-level programming language. Created by Guido van Rossum in 1991.",
        "ai": "Artificial Intelligence is the simulation of human intelligence by machines. Key areas include machine learning, natural language processing, and computer vision.",
        "machine learning": "Machine learning is a subset of AI that enables systems to learn from data. Popular frameworks include TensorFlow and PyTorch.",
        "deep learning": "Deep learning uses neural networks with multiple layers. It has revolutionized image recognition and natural language processing.",
    }
    # 遍历模拟数据，找到匹配的结果
    for key, value in mock_results.items():
        if key in query.lower():
            return value
    return f"No results found for '{query}'"


def read_article(url: str) -> str:
    """模拟读取文章内容

    参数:
        url: 文章 URL

    返回:
        文章内容字符串
    """
    return f"This is the full content of the article at {url}. It contains detailed information about the topic."


# ------------------------------------------------------------
# 第四部分：工具定义
# ------------------------------------------------------------

TOOLS = {
    "web_search": web_search,
    "read_article": read_article,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information. Use this to find relevant articles and data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_article",
            "description": "Read the full content of an article. Use this after finding relevant URLs from search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the article to read",
                    }
                },
                "required": ["url"],
            },
        },
    },
]


# ------------------------------------------------------------
# 第五部分：多步规划 Agent
# ------------------------------------------------------------

def research_agent(topic: str) -> str:
    """研究 Agent：规划 → 搜索 → 阅读 → 总结

    这是今天的核心：多步规划

    流程：
    1. 让 AI 制定研究计划（JSON 格式）
    2. 解析计划，执行每个步骤
    3. 收集所有结果
    4. 让 AI 综合所有结果生成报告

    参数:
        topic: 研究主题

    返回:
        研究报告字符串
    """
    print(f"\n开始研究: {topic}\n")

    # --------------------------------------------------------
    # 第一步：制定计划
    # --------------------------------------------------------
    # 关键点：我们让 AI 返回 JSON 格式的计划
    # response_format={"type": "json_object"} 强制 AI 返回 JSON
    #
    # 什么是 JSON？
    #   JSON = JavaScript Object Notation
    #   一种数据交换格式，用键值对表示数据
    #   例如: {"steps": [{"action": "search", "target": "python"}]}
    print("步骤1: 制定研究计划...")

    plan_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant. Create a research plan for the given topic. "
                           "Return a JSON object with 'steps' array, where each step has "
                           "'action' (search/read) and 'target' (query or URL)."
            },
            {"role": "user", "content": f"Create a research plan for: {topic}"},
        ],
        response_format={"type": "json_object"},  # 强制返回 JSON
    )

    plan_text = plan_response.choices[0].message.content
    print(f"研究计划: {plan_text}\n")

    # 解析 JSON
    # 处理 AI 返回 None 或无效 JSON 的情况
    if not plan_text:
        # AI 返回了 None，使用默认计划
        plan = {"steps": [{"action": "search", "target": topic}]}
    else:
        try:
            plan = json.loads(plan_text)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，使用默认计划
            plan = {"steps": [{"action": "search", "target": topic}]}

    # --------------------------------------------------------
    # 第二步：执行计划
    # --------------------------------------------------------
    # 遍历计划中的每个步骤，执行对应的工具
    research_results = []

    for i, step in enumerate(plan.get("steps", [])):
        # get() 方法：获取字典的值，如果 key 不存在返回默认值
        action = step.get("action", "search")
        target = step.get("target", topic)

        print(f"步骤{i+2}: 执行 {action} - {target}")

        # 根据 action 类型调用不同工具
        if action == "search":
            result = web_search(target)
        elif action == "read":
            result = read_article(target)
        else:
            result = f"Unknown action: {action}"

        research_results.append(result)
        print(f"  结果: {result[:100]}...\n")

    # --------------------------------------------------------
    # 第三步：综合报告
    # --------------------------------------------------------
    # 把所有搜索结果合并成一个字符串，让 AI 综合生成报告
    print("步骤N: 生成研究报告...")

    context = "\n\n".join(research_results)

    report_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant. Synthesize the following research results into a comprehensive report."
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nResearch Results:\n{context}\n\nPlease write a comprehensive report:"
            },
        ],
    )

    report = report_response.choices[0].message.content
    return report


# ------------------------------------------------------------
# 第六部分：主程序
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Web Research Agent 启动\n")

    while True:
        topic = input("输入研究主题 (quit 退出): ")
        if topic.strip().lower() == "quit":
            print("再见！")
            break

        report = research_agent(topic)
        print(f"\n{'='*50}")
        print("研究报告:")
        print('='*50)
        print(report)
        print()
