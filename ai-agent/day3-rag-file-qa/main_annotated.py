# ============================================================
# Day 3: RAG File Q&A — 详细注释版
# ============================================================
#
# RAG = Retrieval-Augmented Generation（检索增强生成）
#
# 核心思路：
#   1. 先把文档切成小块
#   2. 把每个块转成向量（一串数字）
#   3. 用户提问时，把问题也转成向量
#   4. 找到和问题向量最相似的文档块
#   5. 把这些块塞进 prompt，让 AI 基于这些内容回答
#
# 为什么需要 RAG？
#   - AI 的知识有截止日期，不知道最新信息
#   - AI 不知道你公司的内部文档
#   - RAG 让 AI 能"查阅资料"后回答，而不是凭记忆编造


# ------------------------------------------------------------
# 第一部分：导入模块
# ------------------------------------------------------------

# os: 读取环境变量
import os

# numpy: 数学计算库，用于向量运算
# np.array: 创建数组（向量）
# np.dot: 向量点积
# np.linalg.norm: 向量长度（范数）
import numpy as np

# dotenv: 加载 .env 文件
from dotenv import load_dotenv

# openai: 调用 OpenRouter API
from openai import OpenAI


# ------------------------------------------------------------
# 第二部分：初始化
# ------------------------------------------------------------

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# 聊天模型
MODEL = "openai/gpt-oss-120b:free"

# 嵌入模型 — 用于把文本转成向量
# 嵌入模型和聊天模型是不同的
# 嵌入模型只负责把文字变成一串数字（向量），不负责聊天
EMBEDDING_MODEL = "openai/text-embedding-ada-002"


# ------------------------------------------------------------
# 第三部分：读取文件
# ------------------------------------------------------------

def read_file(file_path: str) -> str:
    """读取文本文件内容

    参数:
        file_path: 文件路径

    返回:
        文件内容字符串
    """
    # open() 打开文件
    # "r" 表示读取模式（read）
    # encoding="utf-8" 指定编码，防止中文乱码
    # with 语句确保文件用完后自动关闭（Day 1 知识点）
    with open(file_path, "r", encoding="utf-8") as f:
        # .read() 读取文件全部内容
        return f.read()


# ------------------------------------------------------------
# 第四部分：文本分块（Chunking）
# ------------------------------------------------------------

def split_into_chunks(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    """把长文本切成小块

    为什么要分块？
        - 嵌入模型对输入长度有限制
        - 太长的文本，向量化后信息会被"稀释"
        - 分块后，每个块的语义更集中，检索更精准

    参数:
        text: 要分块的文本
        chunk_size: 每块的字符数（默认 200）
        overlap: 相邻块的重叠字符数（默认 50）

    返回:
        分块后的字符串列表

    为什么需要 overlap（重叠）？
        如果不重叠，一个句子可能被切成两半，语义断裂
        重叠可以保证相邻块之间有连续性
    """
    chunks = []
    start = 0

    # while 循环：每次从 start 位置取 chunk_size 个字符
    while start < len(text):
        end = start + chunk_size
        # text[start:end] 是 Python 的切片语法
        # 取从 start 到 end（不含 end）的子字符串
        chunks.append(text[start:end])
        # 下一块的起始位置 = 当前结束位置 - 重叠长度
        start = end - overlap

    return chunks


# ------------------------------------------------------------
# 第五部分：向量化（Embedding）
# ------------------------------------------------------------

def get_embedding(text: str) -> list[float]:
    """把文本转成向量（一串数字）

    什么是"向量"（Embedding）？
        向量是一串浮点数，例如 [0.1, -0.3, 0.5, ...]
        它代表了文本的"语义"
        意思相近的文本，向量也相近
        意思不同的文本，向量距离远

    为什么用向量？
        计算机不懂文字，但懂数字
        把文字变成数字后，就可以用数学方法计算"相似度"

    参数:
        text: 要向量化的文本

    返回:
        向量（浮点数列表）
    """
    # 调用嵌入模型 API
    # 注意：这里用的是 embeddings.create，不是 chat.completions.create
    # 嵌入模型专门负责把文本变成向量
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    # response.data 是一个列表，取第一个元素的 embedding 属性
    return response.data[0].embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个向量的余弦相似度

    什么是余弦相似度？
        衡量两个向量方向的相似程度
        值域：-1 到 1
        1 = 完全相同方向（语义完全一致）
        0 = 垂直（无关）
        -1 = 完全相反

    公式：
        cos(θ) = (A·B) / (|A| × |B|)

    参数:
        a: 向量 A
        b: 向量 B

    返回:
        相似度分数
    """
    # np.dot(a, b): 向量点积（对应位置相乘再求和）
    # np.linalg.norm(a): 向量长度（所有分量平方和开根号）
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ------------------------------------------------------------
# 第六部分：向量存储和检索
# ------------------------------------------------------------

class VectorStore:
    """简单的向量存储库

    什么是"类"（Class）？
        Day 1 知识点回顾：
        类是蓝图/模板，实例是根据蓝图造出来的对象
        这个类用来存储文档块和对应的向量

    这个类做了什么？
        1. 存储文档块（chunks）和对应的向量（embeddings）
        2. 提供搜索功能：给定查询向量，找到最相似的文档块
    """

    def __init__(self):
        """初始化方法

        __init__ 是 Python 类的"构造函数"
        创建实例时会自动调用
        self 是实例自身
        """
        # self.chunks: 存储所有文档块
        self.chunks: list[str] = []
        # self.embeddings: 存储所有向量
        self.embeddings: list[np.ndarray] = []

    def add(self, chunk: str, embedding: list[float]):
        """添加一个文档块和它的向量

        参数:
            chunk: 文档块文本
            embedding: 对应的向量
        """
        self.chunks.append(chunk)
        # np.array() 把列表转成 numpy 数组，方便数学运算
        self.embeddings.append(np.array(embedding))

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        """搜索最相关的文档块

        参数:
            query_embedding: 查询向量
            top_k: 返回最相关的几个（默认 3 个）

        返回:
            最相关的文档块列表
        """
        query_vec = np.array(query_embedding)
        scores = []

        # 遍历所有向量，计算与查询向量的相似度
        for i, emb in enumerate(self.embeddings):
            score = cosine_similarity(query_vec, emb)
            scores.append((score, i))

        # 按相似度从高到低排序
        scores.sort(reverse=True)

        # 返回 top_k 个最相关的块
        return [self.chunks[i] for _, i in scores[:top_k]]


# ------------------------------------------------------------
# 第七部分：RAG 问答
# ------------------------------------------------------------

def rag_answer(question: str, vector_store: VectorStore) -> str:
    """RAG 完整流程：检索 → 注入 prompt → 生成回答

    流程：
        1. 用户提问
        2. 把问题转成向量
        3. 在向量库中找到最相关的文档块
        4. 把文档块塞进 prompt 的"Context"部分
        5. 发给 AI，让 AI 基于 Context 回答

    参数:
        question: 用户问题
        vector_store: 向量库实例

    返回:
        AI 的回答
    """
    # 1. 把问题向量化
    query_embedding = get_embedding(question)

    # 2. 检索最相关的块
    relevant_chunks = vector_store.search(query_embedding, top_k=3)
    # 把多个块用换行连接成一个字符串
    context = "\n\n".join(relevant_chunks)

    # 3. 构造 prompt，注入检索到的内容
    # 这是 RAG 的关键：把检索到的文档放在 Context 里
    # AI 会基于 Context 来回答，而不是凭自己的知识
    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""

    # 4. 调用 LLM 生成回答
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer based on the given context."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


# ------------------------------------------------------------
# 第八部分：主程序
# ------------------------------------------------------------

if __name__ == "__main__":
    # __name__ == "__main__" 是 Python 的惯例
    # 表示"这个文件是直接运行的，不是被 import 的"
    # 这样当别人 import 这个模块时，下面的代码不会执行

    print("RAG File Q&A 启动中...\n")

    # 1. 读取知识库文件
    text = read_file("knowledge_base.txt")
    print(f"已读取文件，共 {len(text)} 个字符")

    # 2. 分块
    chunks = split_into_chunks(text, chunk_size=200, overlap=50)
    print(f"已分成 {len(chunks)} 个块\n")

    # 3. 向量化并存入向量库
    vector_store = VectorStore()
    for i, chunk in enumerate(chunks):
        # enumerate() 同时获取索引和值
        # i 是索引（0, 1, 2...），chunk 是块内容
        embedding = get_embedding(chunk)
        vector_store.add(chunk, embedding)
        print(f"  已处理块 {i+1}/{len(chunks)}")

    print(f"\n向量库构建完成，共 {len(vector_store.chunks)} 个块\n")

    # 4. 问答循环
    print("输入问题开始查询，输入 quit 退出\n")
    while True:
        question = input("You: ")
        if question.strip().lower() == "quit":
            print("再见！")
            break

        answer = rag_answer(question, vector_store)
        print(f"AI: {answer}\n")
