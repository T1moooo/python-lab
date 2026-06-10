# Day 1 知识点整理

## 1. Python 基础语法

### 1.1 变量和赋值

```python
name = "Alice"
age = 25
```

- `=` 是赋值运算符，把右边的值存到左边的变量里
- Python 不需要声明变量类型，会自动推断
- 命名惯例：用小写字母和下划线，如 `user_name`、`chat_history`

### 1.2 字符串

```python
s1 = "Hello"          # 双引号
s2 = 'Hello'          # 单引号，效果一样
s3 = f"Hi, {name}"    # f-string：花括号里填变量
```

常用方法：
- `.strip()` — 去掉首尾空格和换行
- `.lower()` — 全部变小写
- `.startswith("xxx")` — 判断是否以 xxx 开头

### 1.3 列表（list）

```python
fruits = ["apple", "banana", "cherry"]
fruits.append("date")    # 往末尾添加
first = fruits[0]        # 取第一个元素（索引从 0 开始）
```

- 列表用 `[]` 表示，元素之间用逗号分隔
- `.append()` 往末尾添加
- `[0]` 取第一个，`[1]` 取第二个，`[-1]` 取最后一个

### 1.4 字典（dict）

```python
person = {"name": "Alice", "age": 25}
print(person["name"])     # "Alice"
person["city"] = "Beijing"  # 添加新键值对
```

- 字典用 `{}` 表示，每个元素是 `键: 值`
- 用 `["键名"]` 取值
- `.get("键名")` 取值，键不存在时返回 None 而不是报错

### 1.5 if 条件判断

```python
x = 10
if x > 5:
    print("大于5")
elif x == 5:
    print("等于5")
else:
    print("小于5")
```

- `if` / `elif` / `else` 控制程序走向
- 条件后面要加冒号 `:`
- 缩进（通常 4 个空格）表示"属于这个 if 的代码块"

### 1.6 while 循环

```python
count = 0
while count < 3:
    print(count)
    count += 1
```

- `while` 后面是条件，为 True 就一直循环
- `while True` 是无限循环，需要 `break` 来退出
- `break` — 立刻跳出循环
- `continue` — 跳过本次，继续下一次

### 1.7 for 循环

```python
for item in ["a", "b", "c"]:
    print(item)

for i in range(5):  # 0, 1, 2, 3, 4
    print(i)
```

- `for ... in ...` 遍历列表或其他可迭代对象
- `range(n)` 生成 0 到 n-1 的数字序列

### 1.8 函数

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Alice")
```

- `def` 定义函数，函数名后面跟括号和冒号
- `return` 返回结果
- 调用函数：`函数名(参数)`

---

## 2. Python 进阶概念

### 2.1 from ... import ...

```python
from openai import OpenAI
```

- 从一个包（package）里导入特定的类或函数
- 包 = 别人写好的代码集合，通过 `uv add` 安装
- 和 `import openai` 的区别：`from import` 可以直接用 `OpenAI`，不用写 `openai.OpenAI`

### 2.2 类和实例

```python
# 类是模板
class Dog:
    def __init__(self, name):
        self.name = name

# 实例是根据模板造出来的对象
my_dog = Dog("Buddy")
print(my_dog.name)  # "Buddy"
```

- 类（class）= 蓝图/模板
- 实例（instance）= 根据蓝图造出的具体对象
- `OpenAI(...)` 就是在创建一个 OpenAI 客户端实例

### 2.3 链式调用

```python
reply = response.choices[0].message.content
```

- 用 `.` 一连串访问属性和方法
- 等价于：
  ```python
  choices_list = response.choices
  first_choice = choices_list[0]
  message = first_choice.message
  reply = message.content
  ```

### 2.4 f-string 格式化

```python
name = "Alice"
age = 25
print(f"My name is {name}, I'm {age} years old")
```

- 字符串前面加 `f`
- 花括号 `{}` 里放变量或表达式
- 运行时会被替换成实际值

---

## 3. API 相关概念

### 3.1 什么是 API？

- API = Application Programming Interface（应用程序编程接口）
- 简单理解：API 就是"别人提供给你的一个网址，你往这个网址发请求，它返回数据"
- 类比：餐厅的菜单 — 你点菜（发请求），厨房做菜（处理），服务员上菜（返回数据）

### 3.2 HTTP 请求

- GET — 获取数据（看菜单）
- POST — 提交数据（下单点菜）
- 我们调用 AI 用的是 POST 请求，因为要发送消息给服务器

### 3.3 API Key

- 相当于你的"身份证明"
- 服务器通过 key 知道你是谁，扣你的额度
- 不要把 key 泄露到公开的代码仓库！

### 3.4 环境变量和 .env 文件

**什么是环境变量？**
- 操作系统级别的"键值对"存储
- 程序可以通过 `os.getenv("KEY_NAME")` 读取
- 不会出现在代码文件里，更安全

**什么是 .env 文件？**
- 一个纯文本文件，每行写一个 `KEY=VALUE`
- 用 `python-dotenv` 包的 `load_dotenv()` 加载
- 配合 `.gitignore` 排除，不会被提交到 Git

**完整流程：**
```
.env 文件                    代码
┌──────────────────┐        ┌──────────────────────────┐
│ OPENROUTER_API_KEY│  ──→   │ os.getenv("OPENROUTER_API_KEY") │
│ = sk-or-xxx      │        │                           │
└──────────────────┘        └──────────────────────────┘
     ↑                              ↑
 load_dotenv()              读取环境变量
```

**代码示例：**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

api_key = os.getenv("OPENROUTER_API_KEY")  # 读取环境变量
```

**为什么用 .env？**
- 安全：key 不出现在代码里
- 方便：不同环境（开发/测试/生产）可以用不同的 .env 文件
- 规范：这是业界标准做法

### 3.4 请求和响应的结构

```
请求 = 地址(base_url) + 身份(api_key) + 数据(messages)
响应 = 服务器返回的 JSON 数据
```

### 3.5 Chat Completions API 的消息格式

```json
{
  "messages": [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你的？"},
    {"role": "user", "content": "今天天气怎么样？"}
  ]
}
```

三种角色：
- `system` — 系统指令，设定 AI 行为，用户看不到
- `user` — 用户说的话
- `assistant` — AI 之前说过的话

---

## 4. Agent 核心概念

### 4.1 Agent 是什么？

```
Agent = LLM + 指令 + 工具 + 循环
```

- LLM — 大语言模型，负责"思考"
- 指令 — system prompt，告诉 AI 该怎么做
- 工具 — 函数/代码，让 AI 能执行实际操作（Day 2 会学）
- 循环 — 持续交互，不是一次性的

### 4.2 Day 1 我们实现的是什么？

一个最简单的 Agent：
- ✅ LLM — 通过 OpenRouter 调用
- ✅ 指令 — system prompt
- ❌ 工具 — 还没有（Day 2 加）
- ✅ 循环 — while True 循环

### 4.3 对话历史为什么重要？

```
没有历史：每次请求都是全新的对话，AI 不记得之前说过什么
有历史：   每次请求带上完整对话记录，AI 能理解上下文
```

这就是为什么我们用 `history` 列表来保存所有消息。

---

## 5. 常见问题

### Q: 为什么用 OpenRouter 而不是直接用 OpenAI？
A: OpenRouter 是一个网关，一个 key 可以访问很多模型（OpenAI、Google、Meta 等），方便学习和对比。

### Q: api_key 放在代码里安全吗？
A: 不安全。我们已经改用 `.env` 文件管理 key，这是标准做法。

### Q: 为什么 response.choices[0] 而不是 response.choices？
A: API 支持一次返回多个候选回答（n 参数），我们只取第一个。大多数时候只有一个。

### Q: while True 会不会永远不停？
A: 只要用户输入 `quit` 或按 `Ctrl+C`，程序就会退出。`break` 跳出循环，`Ctrl+C` 强制终止进程。
