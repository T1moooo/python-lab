# ============================================================
# Day 4 练习参考答案
# ============================================================
# 建议：先自己写，卡住了再看这个文件


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


def web_search(query: str) -> str:
    mock_results = {
        "python": "Python is a high-level programming language.",
        "ai": "Artificial Intelligence is the simulation of human intelligence.",
    }
    for key, value in mock_results.items():
        if key in query.lower():
            return value
    return ""


def read_article(url: str) -> str:
    return f"Content of {url}"


TOOLS = {
    "web_search": web_search,
    "read_article": read_article,
}


def research_agent_with_retry(topic: str) -> str:
    print(f"\n开始研究: {topic}\n")

    print("步骤1: 制定研究计划...")
    plan_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Create a research plan. Return JSON with 'steps' array, each step has 'action' and 'target'."},
            {"role": "user", "content": f"Plan for: {topic}"},
        ],
        response_format={"type": "json_object"},
    )

    plan_text = plan_response.choices[0].message.content
    print(f"研究计划: {plan_text}\n")

    if not plan_text:
        plan = {"steps": [{"action": "search", "target": topic}]}
    else:
        try:
            plan = json.loads(plan_text)
        except (json.JSONDecodeError, TypeError):
            plan = {"steps": [{"action": "search", "target": topic}]}

    research_results = []
    max_retries = 3

    for i, step in enumerate(plan.get("steps", [])):
        action = step.get("action", "search")
        target = step.get("target", topic)

        print(f"步骤{i+2}: 执行 {action} - {target}")

        # 重试机制
        result = ""
        for attempt in range(max_retries):
            if action == "search":
                result = web_search(target)
            elif action == "read":
                result = read_article(target)

            if result:  # 成功
                print(f"  尝试 {attempt+1}/{max_retries}: 成功")
                break
            else:  # 失败
                print(f"  尝试 {attempt+1}/{max_retries}: 失败，重试中...")

        if not result:
            print(f"  {max_retries} 次重试后仍失败，跳过此步骤")
            result = "Failed after retries"

        research_results.append(result)
        print(f"  结果: {result[:100]}...\n")

    print("步骤N: 生成研究报告...")
    context = "\n\n".join(research_results)

    report_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Synthesize research results into a report."},
            {"role": "user", "content": f"Topic: {topic}\n\nResults:\n{context}\n\nReport:"},
        ],
    )

    return report_response.choices[0].message.content


if __name__ == "__main__":
    print("练习 Web Research Agent 启动\n")

    while True:
        topic = input("输入研究主题 (quit 退出): ")
        if topic.strip().lower() == "quit":
            print("再见！")
            break

        report = research_agent_with_retry(topic)
        print(f"\n{'='*50}")
        print("研究报告:")
        print('='*50)
        print(report)
        print()
