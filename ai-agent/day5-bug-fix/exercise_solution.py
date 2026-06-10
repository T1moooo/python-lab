# ============================================================
# Day 5 练习参考答案
# ============================================================
# 建议：先自己写，卡住了再看这个文件


import os
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


def call_llm(messages: list, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  API 调用失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
    return ""


def read_code(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def run_tests(test_file: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "测试超时"
    except Exception as e:
        return False, str(e)


def log_message(message: str, log_file: str = "log.txt"):
    """写入日志"""
    # 获取当前时间
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 以追加模式写入文件
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def fix_code(code: str, error_output: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a Python code fixer. Return ONLY the fixed code."
        },
        {
            "role": "user",
            "content": f"Fix this code:\n\n```python\n{code}\n```\n\nTest output:\n```\n{error_output}\n```"
        }
    ]

    fixed_code = call_llm(messages)

    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1]
        fixed_code = fixed_code.split("```")[0]

    return fixed_code.strip()


def bug_fix_agent(code_file: str, test_file: str, max_iterations: int = 5):
    print(f"Bug Fix Agent 启动\n")

    # 记录开始日志
    log_message("Bug Fix Agent 启动")

    for iteration in range(max_iterations):
        print(f"{'='*50}")
        print(f"迭代 {iteration + 1}/{max_iterations}")
        print('='*50)

        code = read_code(code_file)

        # 记录迭代开始日志
        log_message(f"迭代 {iteration + 1} 开始")

        success, output = run_tests(test_file)
        print(f"测试输出:\n{output}")

        if success:
            # 记录成功日志
            log_message("测试通过")
            print("\n✅ 所有测试通过！")
            return True

        # 记录失败日志
        log_message(f"测试失败: {output[:100]}...")

        try:
            fixed_code = fix_code(code, output)
        except Exception as e:
            # 记录错误日志
            log_message(f"API 调用失败: {e}")
            print(f"API 调用失败: {e}")
            continue

        with open(code_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # 记录修复日志
        log_message("已保存修复后的代码")

        print(f"已保存修复后的代码\n")

    log_message("达到最大迭代次数，未能完全修复")
    print(f"\n达到最大迭代次数，未能完全修复。")
    return False


if __name__ == "__main__":
    print("Day 5 练习: Bug Fix Agent\n")

    code_file = "buggy_code.py"
    test_file = "test_buggy_code.py"

    bug_fix_agent(code_file, test_file, max_iterations=5)
