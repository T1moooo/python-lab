import os
import subprocess
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"


# ========== 带重试的 API 调用 ==========

def call_llm(messages: list, max_retries: int = 3) -> str:
    """调用 LLM，带重试机制

    参数:
        messages: 消息列表
        max_retries: 最大重试次数

    返回:
        AI 回复内容
    """
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
                raise  # 最后一次尝试也失败了，抛出异常
    return ""


# ========== 读取代码文件 ==========

def read_code(file_path: str) -> str:
    """读取代码文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ========== 运行测试 ==========

def run_tests(test_file: str) -> tuple[bool, str]:
    """运行测试文件

    返回:
        (是否成功, 输出内容)
    """
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


# ========== 修复代码 ==========

def fix_code(code: str, error_output: str) -> str:
    """让 AI 修复代码

    参数:
        code: 有 bug 的代码
        error_output: 测试输出/错误信息

    返回:
        修复后的代码
    """
    messages = [
        {
            "role": "system",
            "content": """You are a Python code fixer. Given buggy code and test output, fix the code.

Rules:
1. Return ONLY the fixed code, no explanations
2. Keep the same function names and signatures
3. Fix the bugs mentioned in the test output
4. Make sure all tests pass"""
        },
        {
            "role": "user",
            "content": f"""Here is the buggy code:

```python
{code}
```

Here is the test output:
```
{error_output}
```

Please fix the code and return the corrected version."""
        }
    ]

    fixed_code = call_llm(messages)

    # 清理代码（去掉可能的 markdown 标记）
    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1]
        fixed_code = fixed_code.split("```")[0]

    return fixed_code.strip()


# ========== 主程序：执行-观察-修复循环 ==========

def bug_fix_agent(code_file: str, test_file: str, max_iterations: int = 5):
    """Bug 修复 Agent：执行-观察-修复循环

    流程：
    1. 运行测试
    2. 观察结果
    3. 如果失败，让 AI 修复
    4. 重复，直到测试通过或达到最大迭代次数
    """
    print(f"Bug Fix Agent 启动\n")
    print(f"代码文件: {code_file}")
    print(f"测试文件: {test_file}")
    print(f"最大迭代次数: {max_iterations}\n")

    for iteration in range(max_iterations):
        print(f"{'='*50}")
        print(f"迭代 {iteration + 1}/{max_iterations}")
        print('='*50)

        # 1. 读取当前代码
        code = read_code(code_file)
        print(f"\n当前代码:\n{code[:200]}...\n")

        # 2. 运行测试
        print("运行测试...")
        success, output = run_tests(test_file)
        print(f"测试输出:\n{output}")

        # 3. 检查结果
        if success:
            print("\n✅ 所有测试通过！修复完成。")
            return True

        # 4. 测试失败，让 AI 修复
        print("\n❌ 测试失败，让 AI 修复...")

        try:
            fixed_code = fix_code(code, output)
        except Exception as e:
            print(f"API 调用失败: {e}")
            print("等待后重试...")
            continue

        # 5. 保存修复后的代码
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        print(f"已保存修复后的代码\n")

    print(f"\n达到最大迭代次数 ({max_iterations})，未能完全修复。")
    return False


# ========== 主程序 ==========

if __name__ == "__main__":
    print("Day 5: Bug Fix Agent\n")

    # 可以修改为其他文件
    code_file = "buggy_code.py"
    test_file = "test_buggy_code.py"

    bug_fix_agent(code_file, test_file, max_iterations=5)
