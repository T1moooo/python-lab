# ============================================================
# Day 5 练习：添加超时和日志功能
# ============================================================
#
# 目标：巩固异常处理和错误恢复
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   给 bug_fix_agent 添加：
#   1. 日志功能：记录每次迭代的结果到 log.txt
#   2. 超时处理：如果 AI 修复时间太长，跳过本次
#
# 涉及知识点：
#   - 文件写入（open/write）
#   - 异常处理（try/except）
#   - 时间操作（time）


import os
import subprocess
import sys
import time
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


# ========== 练习：添加日志功能 ==========

def log_message(message: str, log_file: str = "log.txt"):
    """写入日志

    参数:
        message: 日志内容
        log_file: 日志文件路径
    """
    # TODO 1: 写入日志
    # 提示：
    #   - 用 open() 以追加模式 ("a") 打开文件
    #   - 获取当前时间：datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #   - 写入格式："[时间] 消息内容\n"
    #   - 用 with 语句确保文件关闭

    # TODO: 补全这里
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    # TODO 2: 记录开始日志
    # 提示：调用 log_message() 记录 "Bug Fix Agent 启动"
    log_message("Bug Fix Agent 启动")

    for iteration in range(max_iterations):
        print(f"{'='*50}")
        print(f"迭代 {iteration + 1}/{max_iterations}")
        print('='*50)

        code = read_code(code_file)

        # TODO 3: 记录迭代开始日志
        # 提示：调用 log_message() 记录 "迭代 X 开始"
        log_message(f"迭代 {iteration + 1} 开始")

        success, output = run_tests(test_file)
        print(f"测试输出:\n{output}")

        if success:
            # TODO 4: 记录成功日志
            # 提示：调用 log_message() 记录 "测试通过"
            log_message("测试通过")
            print("\n✅ 所有测试通过！")
            return True

        # TODO 5: 记录失败日志
        # 提示：调用 log_message() 记录 "测试失败: 输出内容"
        log_message(f"测试失败: {output[:100]}...")

        try:
            fixed_code = fix_code(code, output)
        except Exception as e:
            # TODO 6: 记录错误日志
            # 提示：调用 log_message() 记录 "API 调用失败: 错误信息"
            log_message(f"API 调用失败: {e}")
            print(f"API 调用失败: {e}")
            continue

        with open(code_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # TODO 7: 记录修复日志
        # 提示：调用 log_message() 记录 "已保存修复后的代码"
    
        print(f"已保存修复后的代码\n")

    print(f"\n达到最大迭代次数，未能完全修复。")
    return False


if __name__ == "__main__":
    print("Day 5 练习: Bug Fix Agent\n")

    code_file = "buggy_code.py"
    test_file = "test_buggy_code.py"

    bug_fix_agent(code_file, test_file, max_iterations=5)
