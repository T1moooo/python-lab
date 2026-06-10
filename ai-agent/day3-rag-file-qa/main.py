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


# ========== 第一步：读取文件 ==========

def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ========== 第二步：分块 ==========

def split_into_chunks(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    """把文本按字符数分块，支持重叠"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# ========== 第三步：向量化 ==========

def get_embedding(text: str) -> list[float]:
    """调用 API 获取文本的向量表示"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个向量的余弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ========== 第四步：向量存储和检索 ==========

class VectorStore:
    def __init__(self):
        self.chunks: list[str] = []
        self.embeddings: list[np.ndarray] = []

    def add(self, chunk: str, embedding: list[float]):
        self.chunks.append(chunk)
        self.embeddings.append(np.array(embedding))

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        """找到最相关的 top_k 个块"""
        query_vec = np.array(query_embedding)
        scores = []
        for i, emb in enumerate(self.embeddings):
            score = cosine_similarity(query_vec, emb)
            scores.append((score, i))
        scores.sort(reverse=True)
        return [self.chunks[i] for _, i in scores[:top_k]]


# ========== 第五步：RAG 问答 ==========

def rag_answer(question: str, vector_store: VectorStore) -> str:
    """RAG 流程：检索相关文档 → 注入 prompt → 生成回答"""
    # 1. 把问题向量化
    query_embedding = get_embedding(question)

    # 2. 检索最相关的块
    relevant_chunks = vector_store.search(query_embedding, top_k=3)
    context = "\n\n".join(relevant_chunks)

    # 3. 构造 prompt，注入检索到的内容
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


# ========== 主程序 ==========

if __name__ == "__main__":
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
