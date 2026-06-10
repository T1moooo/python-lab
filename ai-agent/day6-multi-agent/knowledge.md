# Day 6 知识点整理

## 1. 多 Agent 协作

### 1.1 什么是多 Agent？

```
单 Agent：一个 AI 做所有事
多 Agent：多个 AI 各司其职，协作完成任务
```

### 1.2 为什么需要多 Agent？

| 场景 | 单 Agent 的问题 | 多 Agent 的解决方案 |
|------|----------------|-------------------|
| 复杂任务 | 一个 prompt 难以涵盖所有职责 | 分工明确，各司其职 |
| 质量保证 | 自己检查自己，容易有盲区 | 不同角色互相检查 |
| 专业性 | 一个角色难以精通所有领域 | 每个角色专注一个领域 |

### 1.3 多 Agent 协作模式

```
模式1：流水线（Pipeline）
  A → B → C → D
  每个 Agent 处理完传给下一个

模式2：辩论（Debate）
  A ↔ B ↔ C
  多个 Agent 互相讨论，达成共识

模式3：评审（Review）
  A → B → A
  Agent A 做事，Agent B 评审，Agent A 修改

Day 6 使用的是模式3（评审）+ 流水线
```

---

## 2. Agent 角色设计

### 2.1 角色定义的关键要素

```python
AGENTS = {
    "researcher": {
        "name": "研究员",
        "system_prompt": """
你是一个研究员。你的职责是：
1. 分析主题，找出关键信息
2. 收集相关数据和事实
3. 整理成结构化的研究报告

输出格式：
- 主题概述
- 关键要点（3-5个）
- 相关数据/事实
- 总结
"""
    }
}
```

### 2.2 System Prompt 的重要性

| 要素 | 作用 |
|------|------|
| 角色定义 | 告诉 AI "你是谁" |
| 职责说明 | 告诉 AI "你要做什么" |
| 输出格式 | 告诉 AI "怎么输出" |

### 2.3 角色分工示例

```
研究员：收集信息，不写文章
写手：  撰写文章，不评审
审稿人：评审文章，不修改
```

每个角色只做自己的事，避免职责混乱。

---

## 3. 信息传递

### 3.1 Agent 之间如何通信？

```python
# 研究员的输出 → 写手的输入
research = call_llm("researcher", topic)
article = call_llm("writer", f"根据以下资料撰写文章：\n\n{research}")

# 写手的输出 + 审稿人的输出 → 写手的输入
review = call_llm("reviewer", f"请评审以下文章：\n\n{article}")
revised = call_llm("writer", f"原文：\n{article}\n\n审稿意见：\n{review}")
```

### 3.2 信息传递的关键

- 上一个 Agent 的输出是下一个 Agent 的输入
- 需要在 prompt 里明确告诉 AI "这是XXX的输出"
- 保存所有中间结果，方便调试和回溯

---

## 4. 字典（dict）的嵌套

### 4.1 嵌套字典

```python
AGENTS = {
    "researcher": {
        "name": "研究员",
        "system_prompt": "..."
    },
    "writer": {
        "name": "写手",
        "system_prompt": "..."
    }
}

# 访问嵌套字典
AGENTS["researcher"]["name"]          # "研究员"
AGENTS["researcher"]["system_prompt"]  # "..."
```

### 4.2 字典的遍历

```python
# 遍历 key
for role in AGENTS:
    print(role)  # "researcher", "writer", "reviewer"

# 遍历 key-value
for role, config in AGENTS.items():
    print(f"{role}: {config['name']}")
```

---

## 5. Agent 核心概念

### 5.1 Day 1-6 的演进

```
Day 1: Agent = LLM + 指令 + 循环
Day 2: Agent = LLM + 指令 + 工具 + 循环
Day 3: Agent = LLM + 指令 + 工具 + 知识库 + 循环
Day 4: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 循环
Day 5: Agent = LLM + 指令 + 工具 + 知识库 + 规划 + 自我纠错 + 循环
Day 6: 多 Agent 协作 = 多个 Agent + 角色分工 + 信息传递
```

### 5.2 多 Agent 的优势

```
单 Agent：
  - 一个 prompt 要涵盖所有职责
  - 自己检查自己，容易有盲区
  - 难以处理复杂任务

多 Agent：
  - 每个 Agent 专注一个领域
  - 不同角色互相检查
  - 可以处理更复杂的任务
```

---

## 6. 常见问题

### Q: 多 Agent 会消耗更多 token 吗？
A: 是的。每个 Agent 都需要调用 API，token 消耗会成倍增加。

### Q: 如何设计好的角色？
A: 职责要明确、不重叠；输出格式要清晰；prompt 要具体。

### Q: Agent 之间的信息会不会丢失？
A: 会。如果信息太长，可能被截断。需要保存所有中间结果。

### Q: 多 Agent 和单 Agent 哪个效果好？
A: 取决于任务。简单任务单 Agent 更高效；复杂任务多 Agent 更专业。
