# ============================================================
# Day 4 练习：添加重试机制
# ============================================================
#
# 目标：巩固多步规划和错误处理
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   给 research_agent 添加重试机制：
#   - 如果某一步骤执行失败（返回空或错误），自动重试
#   - 最多重试 3 次
#   - 如果 3 次都失败，跳过该步骤继续
#
# 涉及知识点：
#   - 循环（for/while）
#   - 条件判断（if）
#   - 错误处理（try/except）


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
    mock_results = {
        "python": "Python is a high-level programming language.",
        "ai": "Artificial Intelligence is the simulation of human intelligence.",
    }
    for key, value in mock_results.items():
        if key in query.lower():
            return value
    return ""  # 模拟搜索失败


def read_article(url: str) -> str:
    return f"Content of {url}"


TOOLS = {
    "web_search": web_search,
    "read_article": read_article,
}


# ========== 练习：带重试的研究 Agent ==========

def research_agent_with_retry(topic: str) -> str:
    """带重试机制的研究 Agent

    流程：
    1. 制定研究计划
    2. 执行每个步骤（带重试）
    3. 综合报告
    """
    print(f"\n开始研究: {topic}\n")

    # 第一步：制定计划
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

    # 第二步：执行计划（带重试）
    research_results = []
    max_retries = 3

    for i, step in enumerate(plan.get("steps", [])):
        action = step.get("action", "search")
        target = step.get("target", topic)

        print(f"步骤{i+2}: 执行 {action} - {target}")

        # TODO: 添加重试机制
        # 提示：
        #   - 用一个 for 循环尝试 max_retries 次
        #   - 每次尝试执行工具
        #   - 如果结果不为空（成功），就 break 跳出重试循环
        #   - 如果结果为空（失败），打印重试信息，继续下一次尝试
        #   - 如果 3 次都失败，打印失败信息，result 设为 "Failed after retries"

        # TODO: 补全这里
        result = ""
        for attempt in range(max_retries):
            if action == "search":
                result = web_search(target)
            elif action == "read":
                result = read_article(target)
            
            if result:
                print(f"  尝试 {attempt+1}/{max_retries}: 成功")
                break
            else:
                print(f"  尝试 {attempt+1}/{max_retries}: 失败，重试中...")

        if not result:
            print(f"  {max_retries} 次重试后仍失败，跳过此步骤")
            result = "Failed after retries"

        research_results.append(result)
        print(f"  结果: {result[:100]}...\n")

    # 第三步：综合报告
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


# ========== 主程序 ==========

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
