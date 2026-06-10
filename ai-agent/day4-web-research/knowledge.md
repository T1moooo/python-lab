# Day 4 知识点整理

## 1. 多步规划（Multi-Step Planning）

### 1.1 什么是多步规划？

```
单步 Agent：用户提问 → AI 直接回答
多步 Agent：用户提问 → AI 规划步骤 → 逐步执行 → 综合回答
```

### 1.2 为什么需要多步规划？

| 场景 | 单步的问题 | 多步的解决方案 |
|------|-----------|---------------|
| 研究报告 | AI 凭记忆回答，可能编造 | 先搜索真实资料，再综合 |
| 复杂任务 | 一步完成容易出错 | 分解成小步骤，逐步执行 |
| 需要外部数据 | AI 不知道最新信息 | 先获取数据，再分析 |

### 1.3 多步规划的典型流程

```
1. 规划（Plan）
   - 分析任务
   - 确定需要哪些步骤
   - 输出执行计划

2. 执行（Execute）
   - 按计划逐步执行
   - 调用工具获取数据
   - 收集中间结果

3. 综合（Synthesize）
   - 整合所有中间结果
   - 生成最终输出
```

---

## 2. JSON 格式

### 2.1 什么是 JSON？

JSON = JavaScript Object Notation，一种轻量级的数据交换格式。

```json
{
  "name": "Alice",
  "age": 25,
  "hobbies": ["reading", "coding"]
}
```

### 2.2 JSON vs Python 字典

```python
# JSON 字符串（str 类型）
json_str = '{"name": "Alice", "age": 25}'

# Python 字典（dict 类型）
python_dict = {"name": "Alice", "age": 25}

# 互转
import json
data = json.loads(json_str)      # JSON 字符串 → Python 字典
text = json.dumps(python_dict)   # Python 字典 → JSON 字符串
```

### 2.3 强制 AI 返回 JSON

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[...],
    response_format={"type": "json_object"},  # 强制返回 JSON
)
```

为什么要强制 JSON？
- 结构化输出，方便程序解析
- 避免 AI 返回自由文本，难以处理

---

## 3. dict.get() 方法

### 3.1 基本用法

```python
data = {"name": "Alice", "age": 25}

# 直接取值（key 不存在会报错）
data["name"]      # "Alice"
data["email"]     # KeyError!

# 用 get() 取值（key 不存在返回 None 或默认值）
data.get("name")          # "Alice"
data.get("email")         # None
data.get("email", "N/A")  # "N/A"
```

### 3.2 为什么用 get()？

```python
# 危险写法
action = step["action"]  # 如果 step 里没有 "action"，直接报错

# 安全写法
action = step.get("action", "search")  # 没有 "action" 就用默认值 "search"
```

---

## 4. enumerate() 回顾

```python
steps = ["search", "read", "summarize"]

for i, step in enumerate(steps):
    print(f"步骤{i+1}: {step}")
# 步骤1: search
# 步骤2: read
# 步骤3: summarize
```

`enumerate()` 同时获取索引（i）和值（step）。

---

## 5. 字符串切片

```python
text = "Hello, World!"
print(text[:5])    # "Hello"（从开头取到第5个字符）
print(text[7:])    # "World!"（从第7个字符取到结尾）
print(text[:100])  # "Hello, World!"（超出范围不会报错）
```

在代码中：
```python
print(f"  结果: {result[:100]}...")
# 只显示前 100 个字符，避免输出太长
```

---

## 6. Agent 核心概念

### 6.1 Day 1-4 的演进

```
Day 1: Agent = LLM + 指令 + 循环
Day 2: Agent = LLM + 指令 + 工具 + 循环
Day 3: Agent = LLM + 指令 + 工具 + 知识库 + 循环
Day 4: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 循环  ← 新增"规划"
```

### 6.2 规划能力的重要性

没有规划：
- Agent 只能单步响应
- 复杂任务容易出错
- 无法分解任务

有规划：
- Agent 能制定执行计划
- 按步骤逐步执行
- 处理复杂任务

### 6.3 规划的实现方式

```python
# 方式1：让 AI 生成 JSON 计划
plan = ai.generate_plan(topic)

# 方式2：预定义工作流
workflow = [search_step, read_step, summarize_step]

# 方式3：动态规划（AI 根据中间结果决定下一步）
while not done:
    next_step = ai.decide_next(current_state)
    execute(next_step)
```

---

## 7. 常见问题

### Q: AI 生成的 JSON 格式不对怎么办？
A: 用 try-except 捕获 json.JSONDecodeError，使用默认计划作为后备。

### Q: 多步规划会消耗更多 token 吗？
A: 是的。每一步都需要调用 API，token 消耗会增加。但换来的是更准确的结果。

### Q: 如何限制规划的步骤数？
A: 在 system prompt 里说明"最多 3 个步骤"，或者在代码里限制遍历次数。

### Q: 规划和 Chain of Thought 有什么区别？
A: Chain of Thought 是让 AI 分步思考；规划是让 AI 制定可执行的计划，由程序执行。
