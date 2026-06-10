# Day 2 知识点整理

## 1. Function Calling（函数调用）是什么？

### 1.1 核心概念

```
传统聊天：用户 → AI → 文字回复
工具调用：用户 → AI → "我要调用 get_weather" → 你执行函数 → AI 拿到结果 → 文字回复
```

AI 本身不能执行代码，但它可以"决定"什么时候需要调用工具，并告诉你该调用什么函数、传什么参数。

### 1.2 完整流程

```
1. 你告诉 AI：我有这些工具（tools_schema）
2. 用户问：北京天气怎么样？
3. AI 回复：我要调用 get_weather(city="Beijing")
4. 你执行 get_weather("Beijing")，得到 "25°C, sunny"
5. 你把结果告诉 AI
6. AI 回复：北京现在 25°C，晴天
```

关键：AI 不执行函数，它只"请求"你去执行。你是"手脚"，AI 是"大脑"。

---

## 2. JSON Schema（工具描述）

### 2.1 为什么需要 JSON Schema？

AI 不知道你写了哪些函数，你需要用一种标准化格式告诉它：
- 函数叫什么名字
- 函数是干什么的
- 需要哪些参数，每个参数是什么类型

### 2.2 Schema 结构

```python
{
    "type": "function",           # 固定值
    "function": {
        "name": "get_weather",    # 函数名（必须和代码里的函数名一致）
        "description": "...",     # 函数描述（AI 根据这个决定是否调用）
        "parameters": {
            "type": "object",     # 参数是一个对象
            "properties": {       # 每个参数的定义
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]  # 必填参数
        }
    }
}
```

### 2.3 description 的重要性

description 是 AI 决定是否调用工具的依据。写得好坏直接影响 AI 的判断：

```python
# 差：AI 不知道什么时候该用
"description": "A function"

# 好：AI 知道什么时候该用
"description": "Get the current weather for a city. Use this when user asks about weather."
```

---

## 3. 工具调用的返回格式

### 3.1 AI 返回的 tool_calls

当 AI 决定调用工具时，返回的消息里会有 `tool_calls`：

```python
message = response.choices[0].message

# message.tool_calls 是一个列表，可能包含多个工具调用
for tool_call in message.tool_calls:
    print(tool_call.id)                    # 唯一 ID
    print(tool_call.function.name)         # 函数名，如 "get_weather"
    print(tool_call.function.arguments)    # 参数，JSON 字符串，如 '{"city": "Beijing"}'
```

### 3.2 工具结果的格式

执行完工具后，需要把结果以特定格式加入 history：

```python
{
    "role": "tool",              # 固定值
    "tool_call_id": tool_call.id,  # 必须和 tool_call.id 对应
    "content": "结果字符串"        # 工具执行的结果
}
```

---

## 4. Python 语法要点

### 4.1 json.loads()

```python
import json

# JSON 字符串 → Python 字典
data = json.loads('{"city": "Beijing"}')
# 结果: {"city": "Beijing"}

# Python 字典 → JSON 字符串
text = json.dumps({"city": "Beijing"})
# 结果: '{"city": "Beijing"}'
```

为什么需要？
- API 返回的工具参数是 JSON 字符串
- 我们需要转成 Python 字典才能用 `**` 展开传参

### 4.2 ** 展开字典

```python
def greet(name, age):
    return f"Hello {name}, age {age}"

# 这两种写法等价：
greet(name="Alice", age=25)
greet(**{"name": "Alice", "age": 25})
```

`**` 把字典的 key-value 对展开为函数的关键字参数。

### 4.3 函数作为对象

```python
def add(a, b):
    return a + b

# 函数可以赋值给变量
my_func = add
print(my_func(1, 2))  # 3

# 函数可以放进字典
tools = {"add": add}
result = tools["add"](1, 2)  # 3
```

这就是我们用 `TOOLS[func_name](**func_args)` 动态调用函数的原理。

---

## 5. Agent 核心概念：工具调用

### 5.1 Day 1 vs Day 2

```
Day 1: Agent = LLM + 指令 + 循环
Day 2: Agent = LLM + 指令 + 工具 + 循环  ← 新增"工具"
```

### 5.2 为什么工具调用是 Agent 的核心？

没有工具调用：
- AI 只能聊天，不能做事
- 问天气？AI 只能编造答案
- 算数学？AI 可能算错

有工具调用：
- AI 能调用真实 API 获取数据
- AI 能执行代码计算
- AI 能搜索数据库

### 5.3 工具调用 vs 直接调用

```python
# 直接调用：你决定什么时候调用
if "天气" in user_input:
    result = get_weather("Beijing")

# 工具调用：AI 决定什么时候调用
# AI 看了工具描述后，自己判断需要调用哪个
```

工具调用的优势：AI 能根据上下文智能判断，不需要你写 if-else 规则。

---

## 6. 常见问题

### Q: AI 会不会乱调用工具？
A: 可能。AI 有时会误判。可以通过更好的 description 来引导，也可以在代码里加验证。

### Q: 一次可以调用多个工具吗？
A: 可以。`message.tool_calls` 是列表，AI 可能一次请求调用多个工具。

### Q: 工具执行失败怎么办？
A: 把错误信息作为工具结果返回给 AI，AI 会知道出错了并尝试其他方式。

### Q: 为什么需要两次 API 调用？
A: 第一次让 AI 决定是否需要工具，第二次让 AI 根据工具结果生成最终回复。有些模型支持一次调用完成，但分两次更清晰。

### Q: tools_schema 里的 description 用中文还是英文？
A: 取决于模型。大多数模型英文理解更好，建议用英文。
