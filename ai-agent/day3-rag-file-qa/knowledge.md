# Day 3 知识点整理

## 1. RAG 是什么？

### 1.1 核心概念

RAG = Retrieval-Augmented Generation（检索增强生成）

```
传统 AI：用户提问 → AI 凭记忆回答（可能编造）
RAG：    用户提问 → 检索相关文档 → 把文档塞进 prompt → AI 基于文档回答
```

### 1.2 为什么需要 RAG？

| 问题 | RAG 的解决方案 |
|------|---------------|
| AI 知识有截止日期 | 检索最新文档，注入 prompt |
| AI 不知道公司内部文档 | 把内部文档建成向量库 |
| AI 可能编造答案 | 让 AI 基于真实文档回答 |

### 1.3 RAG 完整流程

```
1. 准备阶段（离线）：
   文档 → 分块 → 向量化 → 存入向量库

2. 查询阶段（在线）：
   用户提问 → 问题向量化 → 检索相关块 → 注入 prompt → AI 回答
```

---

## 2. 文档分块（Chunking）

### 2.1 为什么要分块？

- 嵌入模型对输入长度有限制
- 太长的文本，向量化后信息会被"稀释"
- 分块后，每个块的语义更集中，检索更精准

### 2.2 分块策略

```python
# 固定长度分块（最简单）
chunks = [text[i:i+200] for i in range(0, len(text), 200)]

# 带重叠的分块（推荐）
# overlap = 50 表示相邻块重叠 50 个字符
chunks = split_into_chunks(text, chunk_size=200, overlap=50)
```

### 2.3 重叠的作用

```
文本: "Python is a programming language. It was created by Guido."

不重叠（chunk_size=30）:
  块1: "Python is a programming langua"
  块2: "ge. It was created by Guido."
  → "language" 被切成两半！

重叠（chunk_size=30, overlap=10）:
  块1: "Python is a programming langua"
  块2: "nguage. It was created by Gu"
  → 有 10 个字符重叠，语义连续
```

---

## 3. 向量和嵌入（Embedding）

### 3.1 什么是向量？

向量 = 一串数字，例如 `[0.1, -0.3, 0.5, 0.8, ...]`

它代表了文本的"语义"：
- "猫" → `[0.9, 0.1, 0.8, ...]`
- "狗" → `[0.85, 0.15, 0.75, ...]`
- "汽车" → `[0.1, 0.9, 0.2, ...]`

"猫"和"狗"的向量很接近（都是宠物），和"汽车"的向量很远。

### 3.2 嵌入模型

嵌入模型负责把文本变成向量：

```python
response = client.embeddings.create(
    model="openai/text-embedding-ada-002",
    input="Python is a programming language",
)
vector = response.data[0].embedding  # [0.1, -0.3, 0.5, ...]
```

嵌入模型和聊天模型的区别：
| | 嵌入模型 | 聊天模型 |
|---|---|---|
| 输入 | 文本 | 消息列表 |
| 输出 | 向量（数字） | 文字回复 |
| 用途 | 语义搜索、相似度计算 | 对话、问答 |

### 3.3 余弦相似度

衡量两个向量方向的相似程度：

```
cos(θ) = (A·B) / (|A| × |B|)
```

值域：-1 到 1
- 1 = 完全相同方向（语义一致）
- 0 = 垂直（无关）
- -1 = 完全相反

```python
import numpy as np

a = np.array([1, 0, 0])
b = np.array([1, 0, 0])
cosine_similarity(a, b)  # 1.0（完全相同）

c = np.array([0, 1, 0])
cosine_similarity(a, c)  # 0.0（完全无关）
```

---

## 4. 向量数据库

### 4.1 什么是向量数据库？

专门存储和检索向量的数据库。传统数据库用精确匹配，向量数据库用相似度搜索。

### 4.2 常见向量数据库

| 数据库 | 特点 |
|--------|------|
| ChromaDB | 轻量，本地运行，适合学习 |
| FAISS | Facebook 出品，性能好 |
| Pinecone | 云服务，生产级 |
| Weaviate | 开源，功能丰富 |

### 4.3 Day 3 的简化实现

我们用 numpy 手写了一个简单的向量库：
- 存储：列表保存 chunks 和 embeddings
- 检索：遍历所有向量，计算余弦相似度

生产环境会用专门的向量数据库，效率更高。

---

## 5. Python 语法要点

### 5.1 with 语句（上下文管理器）

```python
with open("file.txt", "r") as f:
    content = f.read()
# 离开 with 块后，文件自动关闭
```

等价于：
```python
f = open("file.txt", "r")
try:
    content = f.read()
finally:
    f.close()
```

`with` 更简洁，更安全（不会忘记关闭文件）。

### 5.2 enumerate()

```python
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry
```

`enumerate()` 同时获取索引和值，比手动维护计数器更简洁。

### 5.3 列表推导式

```python
# 传统写法
squares = []
for x in range(5):
    squares.append(x ** 2)

# 列表推导式（更简洁）
squares = [x ** 2 for x in range(5)]
```

### 5.4 join()

```python
chunks = ["Hello", "World", "!"]
result = "\n\n".join(chunks)
# "Hello\n\nWorld\n\n!"
```

`join()` 用分隔符连接列表中的字符串。

### 5.5 类（Class）基础

```python
class VectorStore:
    def __init__(self):      # 构造函数，创建实例时自动调用
        self.chunks = []     # 实例属性

    def add(self, chunk):    # 实例方法
        self.chunks.append(chunk)

store = VectorStore()        # 创建实例
store.add("hello")           # 调用方法
```

---

## 6. Agent 核心概念

### 6.1 Day 1-3 的演进

```
Day 1: Agent = LLM + 指令 + 循环
Day 2: Agent = LLM + 指令 + 工具 + 循环
Day 3: Agent = LLM + 指令 + 工具 + 知识库 + 循环  ← 新增"知识库"
```

### 6.2 RAG 让 Agent 拥有"外部知识"

没有 RAG：
- AI 只能用训练时学到的知识
- 问公司内部文档？不知道
- 问最新新闻？不知道

有 RAG：
- AI 能查阅外部文档
- 基于真实资料回答，减少编造

---

## 7. 常见问题

### Q: chunk_size 设多大合适？
A: 通常 200-1000 字符。太小语义不完整，太大信息稀释。需要根据实际场景调优。

### Q: overlap 设多大合适？
A: 通常是 chunk_size 的 10%-25%。太小可能切断句子，太大浪费存储。

### Q: 嵌入模型选哪个？
A: OpenAI 的 text-embedding-ada-002 是常用选择。也有开源模型如 sentence-transformers。

### Q: 为什么不用关键词搜索？
A: 关键词搜索只能找完全匹配的词。向量搜索能理解语义，"猫"和"猫咪"会被认为是相似的。

### Q: RAG 和微调（Fine-tuning）有什么区别？
A: RAG 是在推理时注入外部知识；微调是在训练时修改模型参数。RAG 更灵活，微调更深入。
