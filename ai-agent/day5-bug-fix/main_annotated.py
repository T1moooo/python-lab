# ============================================================
# Day 5: Bug Fix Agent — 详细注释版
# ============================================================
#
# 今天学习"执行-观察-修复"循环
#
# 流程：
#   1. 执行：运行代码/测试
#   2. 观察：检查输出/错误
#   3. 修复：让 AI 分析并修复代码
#   4. 重复：直到测试通过或达到最大次数
#
# 这是 Agent 的核心能力之一：自我纠错


# ------------------------------------------------------------
# 第一部分：导入模块
# ------------------------------------------------------------

import os
import subprocess  # 用于运行外部命令（如 Python 脚本）
import sys         # 用于获取 Python 解释器路径
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
# 第三部分：带重试的 API 调用
# ------------------------------------------------------------
# 网络请求可能失败（超时、断开等），所以需要重试机制

def call_llm(messages: list, max_retries: int = 3) -> str:
    """调用 LLM，带重试机制

    为什么需要重试？
        - 网络可能不稳定
        - 服务器可能超时
        - 响应可能被截断
        - 重试可以提高成功率

    参数:
        messages: 消息列表
        max_retries: 最大重试次数（默认 3）

    返回:
        AI 回复内容

    异常:
        如果所有重试都失败，抛出最后一个异常
    """
    for attempt in range(max_retries):
        try:
            # 尝试调用 API
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            return response.choices[0].message.content

        except Exception as e:
            # 捕获所有异常（网络错误、超时等）
            print(f"  API 调用失败 (尝试 {attempt+1}/{max_retries}): {e}")

            # 如果是最后一次尝试，抛出异常
            if attempt == max_retries - 1:
                raise

            # 否则继续重试
            # 这里可以加 time.sleep() 等待一下再重试
            # 但为了简单，先直接重试

    return ""


# ------------------------------------------------------------
# 第四部分：读取代码文件
# ------------------------------------------------------------

def read_code(file_path: str) -> str:
    """读取代码文件

    参数:
        file_path: 文件路径

    返回:
        文件内容
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------
# 第五部分：运行测试
# ------------------------------------------------------------

def run_tests(test_file: str) -> tuple[bool, str]:
    """运行测试文件

    subprocess.run() 用于执行外部命令
    这里用来运行 Python 测试脚本

    参数:
        test_file: 测试文件路径

    返回:
        (是否成功, 输出内容)

    subprocess 参数说明:
        - [sys.executable, test_file]: 命令和参数
            - sys.executable: 当前 Python 解释器路径
            - test_file: 要运行的测试文件
        - capture_output=True: 捕获标准输出和错误
        - text=True: 以文本模式返回（不是字节）
        - timeout=30: 超时时间 30 秒
    """
    try:
        # 运行测试
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # 合并标准输出和错误输出
        output = result.stdout + result.stderr

        # returncode: 0 表示成功，非 0 表示失败
        return result.returncode == 0, output

    except subprocess.TimeoutExpired:
        return False, "测试超时"
    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------
# 第六部分：修复代码
# ------------------------------------------------------------

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

    # 调用 AI（带重试）
    fixed_code = call_llm(messages)

    # 清理代码
    # AI 有时会在代码外面加 ```python ... ``` 标记
    # 我们需要去掉这些标记，只保留纯代码
    if "```python" in fixed_code:
        fixed_code = fixed_code.split("```python")[1]
        fixed_code = fixed_code.split("```")[0]

    return fixed_code.strip()


# ------------------------------------------------------------
# 第七部分：主程序：执行-观察-修复循环
# ------------------------------------------------------------

def bug_fix_agent(code_file: str, test_file: str, max_iterations: int = 5):
    """Bug 修复 Agent：执行-观察-修复循环

    这是今天的核心：Execute-Observe-Fix 循环

    流程：
    1. 运行测试
    2. 观察结果
    3. 如果失败，让 AI 修复
    4. 重复，直到测试通过或达到最大迭代次数

    参数:
        code_file: 代码文件路径
        test_file: 测试文件路径
        max_iterations: 最大迭代次数（默认 5）
    """
    print(f"Bug Fix Agent 启动\n")
    print(f"代码文件: {code_file}")
    print(f"测试文件: {test_file}")
    print(f"最大迭代次数: {max_iterations}\n")

    # 主循环：最多尝试 max_iterations 次
    for iteration in range(max_iterations):
        print(f"{'='*50}")
        print(f"迭代 {iteration + 1}/{max_iterations}")
        print('='*50)

        # --------------------------------------------------------
        # 步骤 1：读取当前代码
        # --------------------------------------------------------
        code = read_code(code_file)
        print(f"\n当前代码:\n{code[:200]}...\n")

        # --------------------------------------------------------
        # 步骤 2：运行测试（执行）
        # --------------------------------------------------------
        print("运行测试...")
        success, output = run_tests(test_file)
        print(f"测试输出:\n{output}")

        # --------------------------------------------------------
        # 步骤 3：检查结果（观察）
        # --------------------------------------------------------
        if success:
            # 测试通过，修复完成
            print("\n✅ 所有测试通过！修复完成。")
            return True

        # --------------------------------------------------------
        # 步骤 4：测试失败，让 AI 修复
        # --------------------------------------------------------
        print("\n❌ 测试失败，让 AI 修复...")

        try:
            fixed_code = fix_code(code, output)
        except Exception as e:
            # API 调用失败（网络断开等）
            print(f"API 调用失败: {e}")
            print("等待后重试...")
            continue  # 跳过本次循环，继续下一次

        # --------------------------------------------------------
        # 步骤 5：保存修复后的代码
        # --------------------------------------------------------
        # 把 AI 修复的代码写回文件
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        print(f"已保存修复后的代码\n")

    # 达到最大迭代次数仍未修复
    print(f"\n达到最大迭代次数 ({max_iterations})，未能完全修复。")
    return False


# ------------------------------------------------------------
# 第八部分：主程序
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Day 5: Bug Fix Agent\n")

    # 可以修改为其他文件
    code_file = "buggy_code.py"
    test_file = "test_buggy_code.py"

    bug_fix_agent(code_file, test_file, max_iterations=5)
