import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


# ========== 模拟工具 ==========

def web_search(query: str) -> str:
    """模拟网页搜索"""
    mock_results = {
        "python": "Python is a high-level programming language. Created by Guido van Rossum in 1991.",
        "ai": "Artificial Intelligence is the simulation of human intelligence by machines. Key areas include machine learning, natural language processing, and computer vision.",
        "machine learning": "Machine learning is a subset of AI that enables systems to learn from data. Popular frameworks include TensorFlow and PyTorch.",
        "deep learning": "Deep learning uses neural networks with multiple layers. It has revolutionized image recognition and natural language processing.",
    }
    for key, value in mock_results.items():
        if key in query.lower():
            return value
    return f"No results found for '{query}'"


def read_article(url: str) -> str:
    """模拟读取文章内容"""
    return f"This is the full content of the article at {url}. It contains detailed information about the topic."


# ========== 工具定义 ==========

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


# ========== 多步规划 Agent ==========

def research_agent(topic: str) -> str:
    """研究 Agent：规划 → 搜索 → 阅读 → 总结

    流程：
    1. 让 AI 制定研究计划
    2. 根据计划执行搜索
    3. 阅读搜索结果
    4. 综合所有信息生成报告
    """
    print(f"\n开始研究: {topic}\n")

    # 第一步：制定计划
    print("步骤1: 制定研究计划...")
    plan_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a research assistant. Create a research plan for the given topic. Return a JSON object with 'steps' array, where each step has 'action' (search/read) and 'target' (query or URL)."},
            {"role": "user", "content": f"Create a research plan for: {topic}"},
        ],
        response_format={"type": "json_object"},
    )

    plan_text = plan_response.choices[0].message.content
    print(f"研究计划: {plan_text}\n")

    # 处理 AI 返回 None 或无效 JSON 的情况
    if not plan_text:
        plan = {"steps": [{"action": "search", "target": topic}]}
    else:
        try:
            plan = json.loads(plan_text)
        except (json.JSONDecodeError, TypeError):
            plan = {"steps": [{"action": "search", "target": topic}]}

    # 第二步：执行计划
    research_results = []
    for i, step in enumerate(plan.get("steps", [])):
        action = step.get("action", "search")
        target = step.get("target", topic)

        print(f"步骤{i+2}: 执行 {action} - {target}")

        if action == "search":
            result = web_search(target)
        elif action == "read":
            result = read_article(target)
        else:
            result = f"Unknown action: {action}"

        research_results.append(result)
        print(f"  结果: {result[:100]}...\n")

    # 第三步：综合报告
    print("步骤N: 生成研究报告...")
    context = "\n\n".join(research_results)

    report_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a research assistant. Synthesize the following research results into a comprehensive report."},
            {"role": "user", "content": f"Topic: {topic}\n\nResearch Results:\n{context}\n\nPlease write a comprehensive report:"},
        ],
    )

    report = report_response.choices[0].message.content
    return report


# ========== 主程序 ==========

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
