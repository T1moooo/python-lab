# ============================================================
# Day 3 练习：改进分块策略
# ============================================================
#
# 目标：巩固分块和向量化的概念
#
# 你要做的：
#   1. 先读懂 main.py 的每一行代码
#   2. 在下面的练习代码中，补全标记为 # TODO 的部分
#   3. 运行 `uv run exercise.py` 测试你的代码
#
# 练习内容：
#   实现一个"按句子分块"的函数 split_by_sentence()
#   - 按句号、问号、感叹号分割文本
#   - 每个块包含 1-3 个句子
#   - 如果一个句子太短，就和下一个句子合并
#
# 涉及知识点：
#   - 字符串操作（split, strip）
#   - 列表操作（append, join）
#   - 条件判断（if）


import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openai/gpt-oss-120b:free"
EMBEDDING_MODEL = "openai/text-embedding-ada-002"


# ========== 文件读取 ==========

def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ========== 练习：按句子分块 ==========

def split_by_sentence(text: str, min_length: int = 50) -> list[str]:
    """按句子分块，短句子会合并

    参数:
        text: 要分块的文本
        min_length: 每个块的最小字符数（默认 50）

    返回:
        分块后的字符串列表
    """
    # TODO 1: 用句号、问号、感叹号分割文本
    # 提示：
    #   - 可以用 text.replace("?", "?|").replace("!", "!|").replace(".", ".|")
    #   - 然后用 "|" 分割：text.split("|")
    #   - 或者用正则表达式（进阶）
    #   - 分割后记得 .strip() 去掉首尾空格
    text = text.replace("?", "?|").replace("!", "!|").replace(".", ".|")

    # TODO: 补全这里
    sentences = [s.strip() for s in text.split("|") if s.strip()]

    # TODO 2: 合并短句子
    # 提示：
    #   - 创建一个空列表 chunks
    #   - 创建一个空字符串 current_chunk
    #   - 遍历 sentences：
    #       - 如果 current_chunk 长度 < min_length，就把当前句子追加到 current_chunk
    #       - 否则，把 current_chunk 加入 chunks，重新开始
    #   - 最后别忘了把最后一个 current_chunk 也加入 chunks

    # TODO: 补全这里
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) < min_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


# ========== 向量相关 ==========

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class VectorStore:
    def __init__(self):
        self.chunks: list[str] = []
        self.embeddings: list[np.ndarray] = []

    def add(self, chunk: str, embedding: list[float]):
        self.chunks.append(chunk)
        self.embeddings.append(np.array(embedding))

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        query_vec = np.array(query_embedding)
        scores = []
        for i, emb in enumerate(self.embeddings):
            score = cosine_similarity(query_vec, emb)
            scores.append((score, i))
        scores.sort(reverse=True)
        return [self.chunks[i] for _, i in scores[:top_k]]


# ========== RAG 问答 ==========

def rag_answer(question: str, vector_store: VectorStore) -> str:
    query_embedding = get_embedding(question)
    relevant_chunks = vector_store.search(query_embedding, top_k=3)
    context = "\n\n".join(relevant_chunks)

    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer based on the given context."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


# ========== 主程序 ==========

if __name__ == "__main__":
    print("练习 RAG File Q&A 启动中...\n")

    text = read_file("knowledge_base.txt")
    print(f"已读取文件，共 {len(text)} 个字符")

    # 使用新的分块函数
    chunks = split_by_sentence(text, min_length=50)
    print(f"已分成 {len(chunks)} 个块\n")

    vector_store = VectorStore()
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        vector_store.add(chunk, embedding)
        print(f"  已处理块 {i+1}/{len(chunks)}")

    print(f"\n向量库构建完成，共 {len(vector_store.chunks)} 个块\n")

    print("输入问题开始查询，输入 quit 退出\n")
    while True:
        question = input("You: ")
        if question.strip().lower() == "quit":
            print("再见！")
            break

        answer = rag_answer(question, vector_store)
        print(f"AI: {answer}\n")
