# ============================================================
# Day 3 练习参考答案
# ============================================================
# 建议：先自己写，卡住了再看这个文件


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


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_by_sentence(text: str, min_length: int = 50) -> list[str]:
    """按句子分块，短句子会合并"""

    # 第一步：按句子分割
    # 在句号、问号、感叹号后面加 "|"，然后用 "|" 分割
    # 这样每个句子后面都会带一个标点符号
    text = text.replace(". ", ".|").replace("? ", "?|").replace("! ", "!|")
    sentences = [s.strip() for s in text.split("|") if s.strip()]

    # 第二步：合并短句子
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # 如果当前块还太短，就继续追加
        if len(current_chunk) < min_length:
            current_chunk += " " + sentence
        else:
            # 当前块够长了，加入 chunks，重新开始
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    # 别忘了最后一个块
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


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


if __name__ == "__main__":
    print("练习 RAG File Q&A 启动中...\n")

    text = read_file("knowledge_base.txt")
    print(f"已读取文件，共 {len(text)} 个字符")

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
