# Day 5 知识点整理

## 1. Execute-Observe-Fix 循环

### 1.1 什么是 Execute-Observe-Fix？

```
执行（Execute）→ 观察（Observe）→ 修复（Fix）
    ↑                                    |
    └────────────────────────────────────┘
              重复直到成功
```

这是 Agent 的自我纠错能力：
- 执行代码，看结果
- 如果失败，分析错误
- 修复代码，再试一次

### 1.2 为什么需要这个循环？

| 场景 | 没有循环 | 有循环 |
|------|---------|--------|
| 代码有 bug | 一次失败就停止 | 自动尝试修复 |
| AI 生成的代码 | 可能有错误 | 可以自我纠错 |
| 复杂任务 | 容易卡住 | 持续改进 |

---

## 2. subprocess 模块

### 2.1 什么是 subprocess？

`subprocess` 用于在 Python 中运行外部命令（如其他 Python 脚本）。

```python
import subprocess
import sys

# 运行 Python 脚本
result = subprocess.run(
    [sys.executable, "test.py"],  # 命令和参数
    capture_output=True,          # 捕获输出
    text=True,                    # 文本模式
    timeout=30,                   # 超时时间
)

print(result.stdout)      # 标准输出
print(result.stderr)      # 错误输出
print(result.returncode)  # 返回码（0=成功）
```

### 2.2 参数说明

| 参数 | 含义 |
|------|------|
| `[sys.executable, "test.py"]` | 命令列表：Python 解释器 + 脚本 |
| `capture_output=True` | 捕获 stdout 和 stderr |
| `text=True` | 以字符串返回（不是字节） |
| `timeout=30` | 30 秒超时 |

### 2.3 返回码

```python
result.returncode  # 0 = 成功，非 0 = 失败
```

---

## 3. 异常处理（try/except）

### 3.1 基本语法

```python
try:
    # 可能出错的代码
    result = 1 / 0
except ZeroDivisionError:
    # 处理特定错误
    print("不能除以零")
except Exception as e:
    # 处理所有其他错误
    print(f"发生了错误: {e}")
finally:
    # 无论是否出错都会执行（可选）
    print("清理工作")
```

### 3.2 为什么要用 try/except？

```python
# 不用 try/except：程序崩溃
result = 1 / 0  # ZeroDivisionError，程序终止

# 用 try/except：优雅处理
try:
    result = 1 / 0
except ZeroDivisionError:
    result = 0  # 使用默认值
```

### 3.3 常见异常类型

| 异常 | 原因 |
|------|------|
| `ZeroDivisionError` | 除以零 |
| `FileNotFoundError` | 文件不存在 |
| `TypeError` | 类型错误 |
| `ValueError` | 值错误 |
| `KeyError` | 字典 key 不存在 |
| `IndexError` | 列表索引越界 |

---

## 4. tuple 类型

### 4.1 什么是 tuple？

tuple（元组）是不可变的列表：

```python
# 列表：可变
my_list = [1, 2, 3]
my_list[0] = 10  # 可以修改

# 元组：不可变
my_tuple = (1, 2, 3)
my_tuple[0] = 10  # 报错！不能修改
```

### 4.2 为什么用 tuple？

```python
# 函数返回多个值时，用 tuple
def get_status():
    return True, "成功"  # 返回 tuple

success, message = get_status()  # 解包
```

---

## 5. 字符串清理

### 5.1 去掉 markdown 标记

AI 有时会在代码外面加标记：

```python
# AI 返回的可能是：
"""
```python
def hello():
    print("hello")
```
"""

# 我们需要提取纯代码：
if "```python" in fixed_code:
    fixed_code = fixed_code.split("```python")[1]
    fixed_code = fixed_code.split("```")[0]
```

### 5.2 strip()

```python
text = "  hello  "
text.strip()  # "hello"（去掉首尾空格）
```

---

## 6. Agent 核心概念

### 6.1 Day 1-5 的演进

```
Day 1: Agent = LLM + 指令 + 循环
Day 2: Agent = LLM + 指令 + 工具 + 循环
Day 3: Agent = LLM + 指令 + 工具 + 知识库 + 循环
Day 4: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 循环
Day 5: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 自我纠错 + 循环
```

### 6.2 自我纠错的重要性

没有自我纠错：
- AI 生成代码，一次失败就放弃
- 无法处理意外情况

有自我纠错：
- AI 能观察失败原因
- 分析错误，调整策略
- 持续改进直到成功

---

## 7. 常见问题

### Q: 最大迭代次数设多少合适？
A: 通常 3-5 次。太少可能修不好，太多浪费 token。

### Q: AI 修复的代码还是错的怎么办？
A: 可以在 system prompt 里给更多上下文，或者手动检查后重新运行。

### Q: 如何避免无限循环？
A: 设置最大迭代次数，达到后停止并报告。

### Q: 重试机制应该等多久再重试？
A: 可以用 `time.sleep(1)` 等待 1 秒，避免频繁请求。
